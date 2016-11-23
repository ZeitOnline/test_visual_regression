# -*- coding: utf-8 -*-
import pyramid.view
import zope.component

import zeit.cms.interfaces
import zeit.cms.workflow
import zeit.content.cp.interfaces

import zeit.web.core.interfaces
import zeit.web.core.centerpage
import zeit.web.core.view
import zeit.web.core.utils


class AreaProvidingPaginationMixin(object):

    @zeit.web.reify
    def canonical_url(self):
        area = self.area_providing_pagination
        url = super(AreaProvidingPaginationMixin, self).canonical_url

        if area and area.current_page == 1:
            remove_param = area.page_info(1)['remove_get_param']
            return zeit.web.core.utils.remove_get_params(
                url, remove_param)

        if area and area.current_page > 1:
            get_param = area.page_info(
                area.current_page)['append_get_param']
            return zeit.web.core.utils.add_get_params(url, **get_param)

        return url

    @zeit.web.reify
    def next_page_url(self):
        area = self.area_providing_pagination

        if area and area.current_page < area.total_pages:
            get_param = area.page_info(
                area.current_page + 1)['append_get_param']
            return zeit.web.core.utils.add_get_params(
                self.request.url, **get_param)

    @zeit.web.reify
    def prev_page_url(self):
        area = self.area_providing_pagination

        # suppress page param for page 1
        if area and area.current_page == 2:
            remove_param = area.page_info(
                area.current_page)['remove_get_param']
            return zeit.web.core.utils.remove_get_params(
                self.request.url, remove_param)
        elif area and area.current_page > 2:
            get_param = area.page_info(
                area.current_page - 1)['append_get_param']
            return zeit.web.core.utils.add_get_params(
                self.request.url, **get_param)

    @zeit.web.reify
    def meta_robots(self):
        area = self.area_providing_pagination
        # Prevent continuation pages from being indexed
        if area and area.current_page > 1:
            return 'noindex,follow,noodp,noydir,noarchive'
        return super(AreaProvidingPaginationMixin, self).meta_robots

    @zeit.web.reify
    def pagination(self):
        if self.area_providing_pagination is None:
            return {}
        # Return as many of the same keys in
        # z.w.core.view_article.Article.pagination as make sense here. (Only
        # used by z.w.core.view.Base.webtrekk at the moment.)
        return {
            'current': self.area_providing_pagination.current_page,
            'total': self.area_providing_pagination.total_pages,
            'pager': self.area_providing_pagination.pagination,
            'content_url': self.content_url,
            'next_page_url': self.next_page_url,
            'prev_page_url': self.prev_page_url,
        }


class Centerpage(AreaProvidingPaginationMixin,
                 zeit.web.core.view.CeleraOneMixin, zeit.web.core.view.Base):

    @zeit.web.reify
    def volume(self):
        return zeit.content.volume.interfaces.IVolume(self.context, None)

    @zeit.web.reify
    def volume_navigation(self):
        return {'link': 'https://epaper.zeit.de/abo/diezeit/{!s}/{!s}'.format(
                self.volume.year,
                str(self.volume.volume).zfill(2)),
                'cover': self.volume.covers['printcover']}

    @zeit.web.reify
    def volume_next(self):
        return self.get_volume_info(self.volume.next)

    @zeit.web.reify
    def volume_previous(self):
        return self.get_volume_info(self.volume.previous)

    def get_volume_info(self, volume):
        volume_cp = zeit.content.cp.interfaces.ICenterPage(volume, None)
        if volume_cp:
            return {'link': zeit.web.core.template.create_url(None,
                                                              volume_cp,
                                                              self.request),
                    'label': '{}/{}'.format(str(volume.volume).zfill(2),
                                            volume.year)}

    @zeit.web.reify
    def regions(self):
        """List of regions, the outermost container making up our centerpage.
        :rtype: list
        """
        return [zeit.web.core.centerpage.IRendered(x)
                for x in self.context.values() if x.visible]

    def __iter__(self):
        for region in self.regions:
            for area in region.values():
                for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                        area):
                    if zeit.web.core.view.known_content(teaser):
                        yield teaser

    @zeit.web.reify
    def breadcrumbs(self):
        # No breadcrumbs for homepage
        if self.is_hp:
            return []

        # Default breadcrumbs
        breadcrumbs = super(Centerpage, self).breadcrumbs

        # Search forms
        if zeit.web.core.utils.find_block(
                self.context, module='search-form') is not None:
            try:
                breadcrumbs.extend([(u'Suchergebnisse für "{}"'.format(
                    self.request.GET['q']), None)])
            except KeyError:
                pass
            return breadcrumbs
        # "Angebote" and "Administratives"
        if self.ressort in ('angebote', 'administratives', 'news'):
            # Hamburg news
            if self.ressort == 'news' and self.sub_ressort == 'hamburg':
                nav_item = zeit.web.core.navigation.NAVIGATION_SOURCE.by_name[
                    self.sub_ressort]
                breadcrumbs.extend([(nav_item['text'], nav_item['link'])])
                breadcrumbs.extend([('Aktuell', None)])
                return breadcrumbs
            html_title = zeit.seo.interfaces.ISEO(self.context).html_title
            if html_title is not None:
                breadcrumbs.extend([(html_title, None)])
            else:
                return self.breadcrumbs_by_navigation(breadcrumbs)
        # Video CP
        elif self.ressort == 'video':
            breadcrumbs.extend([('Video', self.context.uniqueId)])
        # Topicpage
        elif self.context.type == 'topicpage':
            self.breadcrumbs_by_navigation(breadcrumbs)
            breadcrumbs.extend([(
                u'Thema: {}'.format(self.supertitle), None)])
        # Archive year index
        elif self.context.type == 'archive-print-year':
            breadcrumbs.extend([
                ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'),
                ("Jahrgang: {}".format(self.context.year), None)])
        # Archive volume index
        elif self.context.type == 'archive-print-volume':
            breadcrumbs.extend([
                ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'),
                ("Jahrgang {}".format(self.context.year),
                    'http://xml.zeit.de/{}/index'.format(self.context.year)),
                ("Ausgabe: {0:02d}".format(self.context.volume or 0), None)])
        # Dynamic folder
        elif zeit.content.dynamicfolder.interfaces.\
                IRepositoryDynamicFolder.providedBy(self.context.__parent__):
            breadcrumbs.extend([(self.title, None)])
        else:
            return self.breadcrumbs_by_navigation(breadcrumbs)

        return breadcrumbs

    @zeit.web.reify
    def area_providing_pagination(self):
        for region in self.regions:
            for area in region.values():
                if zeit.web.core.interfaces.IPagination.providedBy(area):
                    return area
        return None

    @zeit.web.reify
    def webtrekk_content_id(self):
        area = self.area_providing_pagination
        # special case for search results
        if area and area.query_string:
            content_url = self.content_url.replace('http://', '')
            if content_url.endswith('/index'):
                content_url = content_url[:-len('/index')]
            if area.hits:
                basename = 'treffer'
            else:
                basename = 'keine_treffer'
            content_url = '{}/{}'.format(content_url, basename)

            return '{}|{}'.format(self.webtrekk_identifier, content_url)
        else:
            return super(Centerpage, self).webtrekk_content_id

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'homepage'

    @zeit.web.reify
    def has_solo_leader(self):
        try:
            return self.regions[0].values()[0].kind == 'solo'
        except (AttributeError, IndexError):
            return False

    @zeit.web.reify
    def comment_counts(self):
        community = zope.component.getUtility(
            zeit.web.core.interfaces.ICommunity)
        return community.get_comment_counts(*[t.uniqueId for t in self])

    @zeit.web.reify
    def has_cardstack(self):
        kwargs = {'cp:type': 'cardstack'}
        return bool(zeit.web.core.utils.find_block(self.context, **kwargs))

    @zeit.web.reify
    def cardstack_head(self):
        url = super(Centerpage, self).cardstack_head
        return zeit.web.core.utils.update_get_params(url, static='true')

    @zeit.web.reify
    def cardstack_body(self):
        url = super(Centerpage, self).cardstack_body
        return zeit.web.core.utils.update_get_params(url, static='true')


class CenterpagePage(object):

    @zeit.web.reify
    def regions(self):
        if self.area_providing_pagination is None:
            # A paginatable centerpage needs a ranking area.
            raise pyramid.httpexceptions.HTTPNotFound(
                'This centerpage is not paginatable.')

        values = self.context.values()
        if len(values) == 0:
            return []

        # Reconstruct a paginated cp with optional header and ranking area.
        regions = [zeit.web.core.centerpage.Region(
            [zeit.web.core.centerpage.IRendered(
                self.area_providing_pagination)])]

        # We keep any areas of the first region that contain at least one kind
        # of preserve-worthy module.
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        preserved_areas = []
        for mod in conf.get('cp_preserve_modules_on_pagination', '').split():
            module = zeit.web.core.utils.find_block(values[0], module=mod)
            if module:
                area = module.__parent__
                if area not in preserved_areas:
                    preserved_areas.append(
                        zeit.web.core.centerpage.IRendered(area))

        if preserved_areas:
            regions.insert(0, zeit.web.core.centerpage.Region(preserved_areas))

        return regions

    @zeit.web.reify
    def area_providing_pagination(self):
        # Prevent infloop with our tweaked self.regions
        # XXX Is there a better factoring than copy&paste?
        regions = [zeit.web.core.centerpage.IRendered(x)
                   for x in self.context.values()]
        for region in regions:
            for area in region.values():
                if zeit.web.core.interfaces.IPagination.providedBy(area):
                    return area
        return None


@pyramid.view.view_config(
    route_name='json_update_time',
    renderer='jsonp')
def json_update_time(request):
    try:
        resource = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/{}'.format(
                request.matchdict['path']), None)
        if resource is None:
            resource = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/{}'.format(request.matchdict['path']))

        info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        dlps = info.date_last_published_semantic.isoformat()
        dlp = info.date_last_published.isoformat()

    except (AttributeError, KeyError, TypeError):
        dlps = dlp = None
    request.response.cache_expires(5)
    return {'last_published': dlp, 'last_published_semantic': dlps}


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ISitemap,
    renderer='templates/sitemap.html')
class Sitemap(Centerpage):

    def __init__(self, context, request):
        super(Sitemap, self).__init__(context, request)
        self.request.response.content_type = 'application/xml'
