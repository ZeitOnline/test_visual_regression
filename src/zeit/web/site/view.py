# -*- coding: utf-8 -*-
import pyramid.view

import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zeit.cms.content.interfaces

import zeit.web.core.gallery
import zeit.web.core.view
import zeit.web.magazin.view
import zeit.web.site.area.spektrum


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

    if settings['sso_activate']:
        info['login'] = "{}/anmelden?url={}".format(
            settings['sso_url'], destination)
        info['logout'] = "{}/abmelden?url={}".format(
            settings['sso_url'], destination)
    else:
        info['login'] = "{}/user/login?destination={}".format(
            settings['community_host'], destination)
        info['logout'] = "{}/user/logout?destination={}".format(
            settings['community_host'], destination)
    if request.authenticated_userid and 'user' in request.session:
        info['user'] = request.session['user']
        info['profile'] = "{}/user".format(settings['community_host'])
    return info


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

    @zeit.web.reify
    def error(self):
        if 'error' not in self.request.params:
            return
        return self.request.session.pop(self.request.params['error'])
