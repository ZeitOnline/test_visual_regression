# -*- coding: utf-8 -*-
import urlparse
import logging

import pyramid.httpexceptions
import pyramid.view

import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces

import zeit.web.core.gallery
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

    return bool(not zeit.web.magazin.view.is_zmo_content(context, request))


class Base(zeit.web.core.view.Base):

    seo_title_default = (
        u'ZEIT ONLINE | Nachrichten, Hintergründe und Debatten')
    pagetitle_suffix = u' | ZEIT ONLINE'

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        if self.request.params.get('commentstart'):
            target_url = zeit.web.core.template.remove_get_params(
                self.request.url, 'commentstart')
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=target_url)
        if self.request.params.get('page') == 'all':
            target_url = "{}/komplettansicht".format(self.content_url)
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=target_url)

    def banner_toggles(self, name):
        cases = {
            'viewport_zoom': 'tablet',
        }
        return cases.get(name, None)

    @zeit.web.reify
    def breadcrumbs(self):
        return [('Start', 'http://xml.zeit.de/index', 'ZEIT ONLINE')]

    def breadcrumbs_by_title(self, breadcrumbs=None):
        if breadcrumbs is None:
            breadcrumbs = []
        breadcrumbs.extend([(
            self.pagetitle.replace(self.pagetitle_suffix, ''), None)])
        return breadcrumbs

    def breadcrumbs_by_navigation(self, breadcrumbs=None):
        if breadcrumbs is None:
            breadcrumbs = []
        for segment in (self.ressort, self.sub_ressort):
            if segment == u'reisen':
                segment = u'reise'
            try:
                nav_item = zeit.web.core.navigation.navigation_by_name[
                    segment]
                breadcrumbs.extend([(
                    nav_item['text'], nav_item['link'])])
            except KeyError:
                # Segment is no longer be part of the navigation
                next
        return breadcrumbs

    @zeit.web.reify
    def meta_robots(self):
        # Try seo presets first

        if self.seo_robot_override:
            return self.seo_robot_override

        url = self.request.url
        query = urlparse.parse_qs(urlparse.urlparse(url).query)

        # Exclude certain paths from being indexed
        path = self.request.path.startswith

        if path('/angebote') and not path('/angebote/partnersuche'):
            return 'index,nofollow,noodp,noydir,noarchive'
        elif path('/thema') and ('p' not in query or query['p'] == ['1']):
            return 'follow,noarchive'
        elif path('/banner') or path('/test') or path('/templates') \
                or path('/thema'):
                return 'noindex,follow,noodp,noydir,noarchive'
        elif path('/autoren/index'):
            return 'noindex,follow'

        # Exclude certain products and ressorts from being followed
        exclude_products = ('TGS', 'HaBl', 'WIWO', 'GOLEM')

        if self.product_id in exclude_products or (
                self.ressort == 'Fehler' and self.product_id == 'ZEAR'):
                return 'noindex,follow'
        else:
            return 'index,follow,noodp,noydir,noarchive'

    @zeit.web.reify
    def ressort_literally(self):
        if self.is_hp:
            return 'Homepage'

        items = self.navigation.navigation_items
        try:
            item = next((items[key].text, key) for key in items.keys() if (
                        self.ressort in key))
            if self.sub_ressort != '' and items[item[1]].has_children():
                items = items[item[1]].navigation_items
                item = next((items[key].text, key) for key in items.keys() if (
                            self.sub_ressort in key))
        except StopIteration:
            # dirty fallback (for old ressorts not in navigation.xml)
            return self.sub_ressort.upper() if (
                self.sub_ressort != '') else self.ressort.upper()
        return item[0]


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    http_cache=60)
def login_state(request):
    settings = request.registry.settings
    destination = request.params['context-uri'] if request.params.get(
        'context-uri') else 'http://{}'.format(request.host)
    info = {}

    if not request.authenticated_userid and request.cookies.get(
            settings.get('sso_cookie')):
        log.warn("SSO Cookie present, but not authenticated")

    info['login'] = u"{}/anmelden?url={}".format(
        settings['sso_url'], destination)
    info['logout'] = u"{}/abmelden?url={}".format(
            settings['sso_url'], destination)

    if request.authenticated_userid and 'user' in request.session:
        info['user'] = request.session['user']
        info['profile'] = "{}/user".format(settings['community_host'])
    return info


@pyramid.view.view_config(route_name='schlagworte')
def schlagworte(request):
    raise pyramid.httpexceptions.HTTPMovedPermanently(
        u'http://{}/thema/{}'.format(
            request.host, request.matchdict['item'].lower()).encode('utf-8'))


# XXX We should be a little more specific here, ie ICommentableContent
@pyramid.view.view_defaults(
    custom_predicates=(is_zon_content,),
    containment=zeit.cms.content.interfaces.ICommonMetadata)
@pyramid.view.view_config(
    name='comment-form',
    renderer='templates/inc/comments/comment-form.html')
@pyramid.view.view_config(
    name='report-form',
    renderer='templates/inc/comments/report-form.html')
class CommentForm(zeit.web.core.view.Content):

    def __call__(self):
        super(CommentForm, self).__call__()
        # Never ever ever ever cache comment forms
        self.request.response.cache_expires(0)
        return {}

    @zeit.web.reify
    def error(self):
        if 'error' not in self.request.params:
            return
        return self.request.session.pop(self.request.params['error'])


@pyramid.view.view_config(
    route_name='frame_builder',
    renderer='templates/frame_builder.html')
class FrameBuilder(Base):

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/index')
            self.context.advertising_enabled = self.banner_on
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()

    @zeit.web.reify
    def advertising_enabled(self):
        if self.banner_channel:
            return True
        else:
            return False

    @zeit.web.reify
    def banner_channel(self):
        return self.request.GET.get('banner_channel', None)
