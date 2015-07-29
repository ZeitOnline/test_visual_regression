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

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = [('Start', 'http://xml.zeit.de/index', 'ZEIT ONLINE')]
        context_type = getattr(self.context, 'type', self.type)

        def add_breadcrumbs_by_navigation():
            for segment in (self.ressort, self.sub_ressort):
                try:
                    nav_item = zeit.web.core.navigation.navigation_by_name[
                        segment]
                    breadcrumbs.extend([(
                        nav_item['text'], nav_item['link'])])
                except KeyError:
                    # Segment is no longer be part of the navigation
                    next

        def add_default_breadcrumbs():
            breadcrumbs.extend([(
                self.pagetitle.replace(self.pagetitle_suffix, ''), None)])

        # "Angebote" and "Administratives"
        if self.ressort in ('angebote', 'administratives'):
            html_title = zeit.seo.interfaces.ISEO(self.context).html_title
            if html_title is not None:
                breadcrumbs.extend([(html_title, None)])
            else:
                add_default_breadcrumbs()
        # Video index
        elif self.ressort == 'video':
            breadcrumbs.extend([('Video', self.context.uniqueId)])
        # Video
        elif context_type == 'video':
            breadcrumbs.extend([('Video', 'http://xml.zeit.de/video/index')])
            add_breadcrumbs_by_navigation()
            add_default_breadcrumbs()
        # Article
        elif context_type in ('article', 'gallery', 'quiz'):
            # Add breadcrumbs that belong to the navgiation
            add_breadcrumbs_by_navigation()
            # Append page teaser
            page_teaser = self.current_page.teaser
            if len(page_teaser) > 0:
                breadcrumbs.extend([(page_teaser, self.context.uniqueId)])
            else:
                add_default_breadcrumbs()
        # Topicpage
        elif context_type == 'topicpage':
            add_breadcrumbs_by_navigation()
            breadcrumbs.extend([(
                'Thema: {}'.format(self.context.title), None)])
        # Archive year index
        elif context_type == 'archive-print-year':
            breadcrumbs.extend([
                ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'),
                ("Jahrgang: {}".format(self.context.year), None)])
        # Archive volume index
        elif context_type == 'archive-print-volume':
            breadcrumbs.extend([
                ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'),
                ("Jahrgang {}".format(self.context.year),
                    '{}/index'.format(self.content_url.rsplit('/', 2)[0])),
                ("Ausgabe: {}".format(self.context.volume), None)])
        else:
            add_default_breadcrumbs()
        return breadcrumbs


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
