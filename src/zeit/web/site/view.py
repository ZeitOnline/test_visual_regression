# -*- coding: utf-8 -*-
import logging

import pyramid.httpexceptions
import pyramid.view

import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces

import zeit.web.campus.view
import zeit.web.core.gallery
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
                nav_item = zeit.web.core.navigation.NAVIGATION_SOURCE.by_name[
                    segment]
                breadcrumbs.extend([(nav_item['text'], nav_item['link'])])
            except KeyError:
                # Segment is no longer be part of the navigation
                next
        return breadcrumbs

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
                self.product_id in ('TGS', 'HaBl', 'WIWO', 'GOLEM'):
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


@pyramid.view.view_config(route_name='schlagworte')
def schlagworte(request):
    raise pyramid.httpexceptions.HTTPMovedPermanently(
        u'{}thema/{}'.format(
            request.route_path('home'),
            request.matchdict['item'].lower()).encode('utf-8'))


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
class CommentForm(zeit.web.core.view.CommentMixin,
                  zeit.web.core.view.Base):

    def __call__(self):
        result = super(CommentForm, self).__call__()
        # Never ever ever ever cache comment forms
        self.request.response.cache_expires(0)
        return result

    @zeit.web.reify
    def error(self):
        if 'error' not in self.request.params:
            return
        return self.request.session.pop(self.request.params['error'])


@pyramid.view.view_config(
    route_name='framebuilder',
    renderer='templates/framebuilder/framebuilder.html')
class FrameBuilder(zeit.web.core.view.FrameBuilder, Base):

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/index')
            self.context.advertising_enabled = self.banner_on
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()

    @zeit.web.reify
    def ressort(self):
        return self.request.GET.get('ressort', None)
