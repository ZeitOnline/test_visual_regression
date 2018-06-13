# -*- coding: utf-8 -*-
import logging
import urllib

import pyramid.httpexceptions
import zope.component

import zeit.content.rawxml.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces

import zeit.web
import zeit.web.core.security
import zeit.web.core.view


log = logging.getLogger(__name__)


class Base(zeit.web.core.view.Base):

    seo_title_default = (
        u'ZEIT ONLINE | Nachrichten, Hintergründe und Debatten')
    pagetitle_suffix = u' | ZEIT ONLINE'

    nav_show_ressorts = True
    nav_show_search = True

    def __init__(self, context, request):
        super(Base, self).__init__(context, request)
        if self.request.params.get('commentstart'):
            target_url = zeit.web.core.template.remove_get_params(
                self.request.url, 'commentstart')
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=target_url)
        if self.request.params.get('page') == 'all':
            # XXX response.location should urlencode itself, but that's really
            # hard to do generally (e.g. already urlencoded query parameters),
            # so we do it from the outside where we still have enough context.
            target_url = u'{}/komplettansicht'.format(
                urllib.quote(self.content_url.encode('utf-8'), safe='/:?&='))
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=target_url)

    @zeit.web.reify
    def meta_robots(self):
        # Prevent certain paths, products and edgecases from being indexed
        path = self.request.path.startswith

        if path('/angebote') and not path('/angebote/partnersuche'):
            return 'index,nofollow,noarchive'

        if (self.ressort == 'Fehler' and self.product_id == 'ZEAR') or \
            path('/banner') or \
            path('/test') or \
            path('/templates') or \
            path('/autoren/register') or \
            self.shared_cardstack_id or \
                self.product_id in ('TGS', 'HaBl', 'WIWO', 'GOLEM',
                                    'tonic-magazin', 'edition-f'):
            return 'noindex,follow,noarchive'

        return super(Base, self).meta_robots

    @zeit.web.reify
    def ressort_literally(self):
        if self.is_hp:
            return 'Homepage'

        if self.ressort == 'administratives':
            return ''

        items = self.navigation
        try:
            item = next((items[key].text, key) for key in items.keys() if (
                        self.ressort in key))
            if self.sub_ressort != '' and len(items[item[1]]):
                items = items[item[1]]
                item = next((items[key].text, key) for key in items.keys() if (
                            self.sub_ressort in key))
        except StopIteration:
            # dirty fallback (for old ressorts not in navigation.xml)
            return self.sub_ressort.capitalize() if (
                self.sub_ressort != '') else self.ressort.capitalize()
        return item[0]

    @zeit.web.reify
    def shared_cardstack_id(self):
        return self.request.GET.get('stackId', '') or None

    @zeit.web.reify
    def include_optimize(self):
        return None


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=site',
    http_cache=60)
@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    custom_predicates=((lambda c, r: 'for' not in r.GET.keys()),),
    http_cache=60)  # Perhaps needed for bw compat? (ND)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)


@zeit.web.view_config(
    context=zeit.content.rawxml.interfaces.IUserDashboard,
    renderer='templates/dashboard_user.html')
class UserDashboard(Base):

    advertising_enabled = False

    def __init__(self, context, request):
        super(UserDashboard, self).__init__(context, request)
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if not self.request.user:
            raise pyramid.httpexceptions.HTTPFound(
                location=u'{}/anmelden?{}'.format(
                    conf.get('sso_url'),
                    urllib.urlencode({'url': self.request.url})))
        # XXX There's nothing in ICommonMetadata that's relevant for the
        # dashboard (and rawxml objects rightfully don't have it), but
        # `layout.html` and `view.Base` expect it, which feels somewhat wrong
        # and should be cleaned up; for now we pacify them with default values.
        zeit.cms.browser.form.apply_default_values(
            self.context, zeit.cms.content.interfaces.ICommonMetadata,
            set_none=True)

    @zeit.web.reify
    def title(self):
        return self.context.xml.title

    # Don't call this `supertitle` so it doesn't show up in the browser title
    @zeit.web.reify
    def kicker(self):
        return self.context.xml.kicker

    def dashboard_sections(self, class_):
        return [self._parse_section(section) for section
                in self.context.xml.xpath('//section[@class="%s"]' % class_)]

    def _parse_section(self, section):
        result = dict(section.attrib)
        result['links'] = []
        for node in section.xpath('link'):
            link = dict(node.attrib)
            link['text'] = node.text
            result['links'].append(link)
        return result


@zeit.web.view_config(route_name='schlagworte')
def schlagworte(request):
    try:
        page = int(request.matchdict['subpath'].lstrip('index/seite-'))
    except (TypeError, ValueError):
        page = 0
    try:
        result = pyramid.httpexceptions.HTTPMovedPermanently(
            u'{}thema/{}{}'.format(
                request.route_path('home').lower(),
                request.matchdict['item'].lower(),
                '?p={}'.format(page) if page > 1 else ''
            ).encode('utf-8'))
    except:
        result = pyramid.httpexceptions.HTTPBadRequest()
    raise result


@zeit.web.view_config(
    route_name='framebuilder',
    renderer='templates/framebuilder/framebuilder.html')
class FrameBuilder(zeit.web.core.view.FrameBuilder, Base):

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/index')
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()


# http_cache time is determined approximately in order to provide some caching
# but don't interrupt the CvD's work by rendering dated content.
@zeit.web.view_config(
    route_name='breaking_news',
    renderer='templates/inc/breaking_news.html',
    http_cache=3)
class BreakingNewsBanner(zeit.web.core.block.BreakingNews):

    def __init__(self, context, request):
        super(BreakingNewsBanner, self).__init__()

    def __call__(self):
        return {}
