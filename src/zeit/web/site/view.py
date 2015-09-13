# -*- coding: utf-8 -*-
import urlparse
import logging

import pyramid.view

import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zeit.cms.content.interfaces

import zeit.web.core.gallery
import zeit.web.core.view
import zeit.web.magazin.view
import zeit.web.site.area.spektrum


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
        else:
            return 'index,follow,noodp,noydir,noarchive'


@pyramid.view.view_config(
    route_name='spektrum-kooperation',
    renderer='templates/inc/area/spektrum.html')
def spektrum_hp_feed(request):
    # add CORS header to allow ESI JS drop-in
    request.response.headers.add(
        'Access-Control-Allow-Origin', '*')
    request.response.cache_expires(60)
    return {
        'esi_toggle': True,
        'area': zeit.web.site.area.spektrum.HPFeed(),
        'parquet_position': request.params.get('parquet-position')
    }


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html')
def login_state(request):
    settings = request.registry.settings
    destination = request.params['context-uri'] if request.params.get(
        'context-uri') else 'http://{}'.format(request.host)
    info = {}

    if not request.authenticated_userid and request.cookies.get(
            settings.get('sso_cookie')):
        log.warn("SSO Cookie present, but not authenticated")

    if settings['sso_activate']:
        info['login'] = u"{}/anmelden?url={}".format(
            settings['sso_url'], destination)
        info['logout'] = u"{}/abmelden?url={}".format(
            settings['sso_url'], destination)
    else:
        info['login'] = u"{}/user/login?destination={}".format(
            settings['community_host'], destination)
        info['logout'] = u"{}/user/logout?destination={}".format(
            settings['community_host'], destination)
    if request.authenticated_userid and 'user' in request.session:
        info['user'] = request.session['user']
        info['profile'] = "{}/user".format(settings['community_host'])
    return info


@pyramid.view.view_config(route_name='schlagworte')
def schlagworte(request):
    raise pyramid.httpexceptions.HTTPMovedPermanently(
        'http://{}/thema/{}'.format(
            request.host, request.matchdict['item'].lower()))


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
