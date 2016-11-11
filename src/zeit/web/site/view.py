# -*- coding: utf-8 -*-
import logging
import urllib

import pyramid.httpexceptions
import pyramid.view

import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces

import zeit.web.campus.view
import zeit.web.core.security
import zeit.web.core.view
import zeit.web.magazin.view


log = logging.getLogger(__name__)


def is_zon_content(context, request):
    """Custom predicate to verify, if this can be rendered via zeit.web
    :rtype: bool
    """

    # We might need to evaluate, if we have a rebrush_website_content again at
    # some point. So this is, how it would be done. (ron)
    #  return bool(getattr(context, 'rebrush_website_content', False)) and (
    #    not zeit.web.magazin.view.is_zmo_content(context, request))

    return bool(not zeit.web.magazin.view.is_zmo_content(context, request) and
                not zeit.web.campus.view.is_zco_content(context, request))


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

    def banner_toggles(self, name):
        cases = {
            'viewport_zoom': 'tablet',
        }
        return cases.get(name, None)

    @zeit.web.reify
    def meta_robots(self):
        # Prevent certain paths, products and edgecases from being indexed
        path = self.request.path.startswith

        if path('/angebote') and not path('/angebote/partnersuche'):
            return 'index,nofollow,noodp,noydir,noarchive'

        if (self.ressort == 'Fehler' and self.product_id == 'ZEAR') or \
            path('/banner') or \
            path('/test') or \
            path('/templates') or \
            path('/autoren/register') or \
            self.shared_cardstack_id or \
                self.product_id in ('TGS', 'HaBl', 'WIWO', 'GOLEM',
                                    'tonic-magazin', 'edition-f'):
            return 'noindex,follow,noodp,noydir,noarchive'

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


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=site',
    http_cache=60)
@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    custom_predicates=((lambda c, r: 'for' not in r.GET.keys()),),
    http_cache=60)  # Perhaps needed for bw compat? (ND)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)

@pyramid.view.view_config(
    route_name='dashboard_user',
    renderer='templates/inc/module/dashboard_user.html',
    http_cache=60)
class UserDashboard(zeit.web.core.view.FrameBuilder, Base):
    def __init__(self, context, request):
        super(UserDashboard, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/index')
            self.dashboard_user = self.dashboard_user()
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()

    def dashboard_user(self):
        from lxml import etree
        xml = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/config/dashboard_user.xml', None).data
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        sections_xml = etree.fromstring(xml.encode('utf-8'), parser=parser).iterfind('section')
        return {
            'title': etree.fromstring(xml).find('title').text,
            'kicker': etree.fromstring(xml).find('kicker').text,
            'sections': {section.get('id'): self._iter(section) for section in sections_xml},
        }

    def _iter(self, section):
        links = section.iterfind('link')
        lnks = [{'text': link.text, 'attributes': link.attrib} for link in links]
        sctn = section.attrib
        return {'section_atts': sctn, 'links': lnks}

@pyramid.view.view_config(route_name='schlagworte')
def schlagworte(request):
    try:
        page = int(request.matchdict['subpath'].lstrip('index/seite-'))
    except (TypeError, ValueError):
        page = 0
    raise pyramid.httpexceptions.HTTPMovedPermanently(
        u'{}thema/{}{}'.format(
            request.route_path('home').lower(),
            request.matchdict['item'].lower(),
            '?p={}'.format(page) if page > 1 else ''
        ).encode('utf-8'))


@pyramid.view.view_config(
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
