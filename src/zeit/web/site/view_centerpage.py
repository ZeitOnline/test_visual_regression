# -*- coding: utf-8 -*-
import collections
import logging
import uuid

import grokcore.component
import lxml.etree
import pyramid.view
import zope.component
import zope.component.interfaces
import zope.interface

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces

import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.navigation
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.core.centerpage
import zeit.web.site.module.buzzbox
import zeit.web.site.module.printbox


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.web.core.interfaces.IBlock)
class LegacyModule(
        zeit.web.core.centerpage.Module, zeit.web.core.utils.nslist):

    def __init__(self, arg, **kw):
        zeit.web.core.utils.nslist.__init__(self, [v for v in arg if v])
        self.layout = kw.pop('layout', 'default')
        self.type = kw.pop('type', 'teaser')
        self.__parent = kw.pop('parent', None)

    def __hash__(self):
        if getattr(self.layout, 'id', None):
            return hash((self.layout.id, id(self)))
        else:
            raise NotImplementedError()

    def __repr__(self):
        return object.__repr__(self)


@zope.interface.implementer(zeit.content.cp.interfaces.IArea)
class LegacyArea(collections.OrderedDict, zeit.content.cp.area.AreaFactory):

    def __init__(self, arg, **kw):
        collections.OrderedDict.__init__(
            self, [('id-{}'.format(uuid.uuid1()), v) for v in arg if v])
        self.kind = kw.pop('kind', 'solo')
        self.xml = kw.pop('xml', self.get_xml())
        self.automatic = kw.pop('automatic', False)
        self.__parent__ = kw.pop('parent', None)

        for key in kw:
            try:
                assert not hasattr(self, key)
                setattr(self, key, kw[key])
            except:
                continue

    def append(self, value):
        self['id-{}'.format(uuid.uuid1())] = value

    def __hash__(self):
        if self.kind:
            return hash((self.kind, id(self)))
        else:
            raise NotImplementedError()

    def __repr__(self):
        return object.__repr__(self)

    # XXX This is really crude, but since these Legacy-classes throw away
    # their vivi-side objects, we can't get to the interfaces anymore,
    # so a full re-implementation is just plain impossible.
    # So we hard-code the only use-case that this should ever be called for,
    # which is ITeaseredContent.
    def select_modules(self, *interfaces):
        for module in zeit.content.cp.interfaces.IRenderedArea(self).values():
            if getattr(module, 'type', None) == 'teaser':
                yield module


@zope.interface.implementer(zeit.content.cp.interfaces.IRegion)
class LegacyRegion(LegacyArea, zeit.content.cp.area.RegionFactory):

    def __init__(self, arg, **kw):
        LegacyArea.__init__(self, arg, **kw)


@grokcore.component.adapter(
    zeit.content.cp.interfaces.IArea,
    zeit.content.cp.interfaces.ITeaserBlock)
@grokcore.component.implementer(
    zeit.content.cp.interfaces.IRenderedArea)
class RenderedLegacyArea(LegacyArea):

    def __init__(self, area, block):
        area.count = int(block.xml.get('display_amount', 3))
        uid = unicode(block.xml.find('./referenced_cp'))
        area.referenced_cp = zeit.cms.interfaces.ICMSContent(uid, None)
        auto = zeit.content.cp.interfaces.IRenderedArea(area)
        # XXX We really should call auto.values() here instead of private API.
        auto._v_try_to_retrieve_content = True
        auto._v_retrieved_content = 0
        values = auto._query_centerpage()[:area.count]

        lids = [block.layout.id] + area.count * ['zon-parquet-small']
        modules = [LegacyModule(
            [t], layout=lids.pop(0), parent=self) for t in values]
        LegacyArea.__init__(self, modules, kind='parquet', is_teaserbar=True)

        self.read_more = block.read_more
        self.read_more_url = block.read_more_url
        self.title = block.title
        self.referenced_cp = area.referenced_cp


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/centerpage_advertorial.html')
@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class Centerpage(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):
    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def has_cardstack(self):
        kwargs = {'cp:type': 'cardstack'}
        return bool(zeit.web.core.utils.find_block(self.context, **kwargs))

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
                u'Thema: {}'.format(self.context.title), None)])
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
                ("Ausgabe: {0:02d}".format(self.context.volume), None)])
        # Dynamic folder
        elif zeit.content.dynamicfolder.interfaces.\
                IRepositoryDynamicFolder.providedBy(self.context.__parent__):
            breadcrumbs.extend([(self.title, None)])
        else:
            return self.breadcrumbs_by_navigation(breadcrumbs)

        return breadcrumbs

    @zeit.web.reify
    def ressort(self):
        return 'homepage' if self.is_hp else super(Centerpage, self).ressort

    @zeit.web.reify
    def area_ranking(self):
        for region in self.regions:
            for area in region.values():
                if zeit.web.core.interfaces.IPagination.providedBy(area):
                    return area
        return None

    @zeit.web.reify
    def next_page_url(self):
        ranking = self.area_ranking
        if ranking is None:
            return None
        if ranking.current_page < len(ranking.pagination):
            return zeit.web.core.template.append_get_params(
                self.request, p=ranking.current_page + 1)

    @zeit.web.reify
    def prev_page_url(self):
        ranking = self.area_ranking
        if ranking is None:
            return None
        # suppress page param for page 1
        if ranking.current_page == 2:
            return zeit.web.core.template.remove_get_params(
                self.request.url, 'p')
        elif ranking.current_page > 2:
            return zeit.web.core.template.append_get_params(
                self.request, p=ranking.current_page - 1)

    @zeit.web.reify
    def cardstack_head(self):
        url = super(Centerpage, self).cardstack_head
        return zeit.web.core.utils.update_query(url, static='true')

    @zeit.web.reify
    def cardstack_body(self):
        url = super(Centerpage, self).cardstack_body
        return zeit.web.core.utils.update_query(url, static='true')


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_paginated),
    renderer='templates/centerpage.html')
class CenterpagePage(Centerpage):

    @zeit.web.reify
    def regions(self):
        if self.area_ranking is None:
            # A paginatable centerpage needs a ranking area.
            raise pyramid.httpexceptions.HTTPNotFound(
                'This centerpage is not paginatable.')

        values = self.context.values()
        if len(values) == 0:
            return []

        # Reconstruct a paginated cp with optional header and ranking area.
        regions = [LegacyRegion([zeit.web.core.centerpage.IRendered(
            self.area_ranking)])]

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
            regions.insert(0, LegacyRegion(preserved_areas))

        return regions

    @zeit.web.reify
    def area_ranking(self):
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
    name='area',
    context=zeit.content.cp.interfaces.ICP2015,
    renderer='templates/inc/area/includer.html')
class CenterpageArea(Centerpage):

    def __init__(self, context, request):
        if not request.subpath:
            raise pyramid.httpexceptions.HTTPNotFound()

        self.context = None
        self.request = request

        self.request.response.headers.add('X-Robots-Tag', 'noindex')

        self.comment_counts = {}
        self.has_solo_leader = False

        name = request.subpath[-1]

        def uid_cond(index, area):
            return area.uniqueId.rsplit('/', 1)[-1] == name

        def index_cond(index, area):
            try:
                return index == int(name.lstrip(u'no-'))
            except ValueError:
                raise pyramid.httpexceptions.HTTPNotFound('Area not found')

        if name.startswith('id-'):
            condition = uid_cond
        elif name.startswith('no-'):
            condition = index_cond

        index = 1
        for region in context.values():
            for area in region.values():
                if condition(index, area):
                    self.context = zeit.web.core.centerpage.get_area(area)
                    return
                else:
                    index += 1

    def __call__(self):
        return {
            'area': self.context,
            'region_loop': {'index': 1}
        }


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.IStoryStream,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/storystream.html')
class Storystream(Centerpage):
    """Main view class for ZEIT ONLINE storystreams."""

    atom_meta = {
        'count': None,
        'oldest_date': None,
        'latest_date': None
    }

    countable_atom_types = [zeit.content.cp.interfaces.ITeaserBlock]

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self.prepare_atom_meta()

    def prepare_atom_meta(self):

        atom_counter = 0
        oldest_atom = None
        latest_atom = None

        regions = self.regions
        for region in regions:
            areas = region.values()
            for area in areas:
                for module in area.select_modules(*self.countable_atom_types):
                    atom_counter += 1

                    # OPTIMIZE: this traversal is redundant (also done inside
                    # the template). Maybe we should store the teaser
                    # object into the module?
                    teaser = zeit.web.core.template.first_child(module)
                    if ((oldest_atom is None) or
                            (teaser.tldr_date is not None and
                                oldest_atom > teaser.tldr_date)):
                        oldest_atom = teaser.tldr_date

                    if ((latest_atom is None) or
                            (teaser.tldr_date is not None and
                                latest_atom < teaser.tldr_date)):
                        latest_atom = teaser.tldr_date

        self.atom_meta['count'] = atom_counter
        self.atom_meta['oldest_date'] = oldest_atom
        self.atom_meta['latest_date'] = latest_atom


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/centerpage_advertorial.html')
@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class LegacyCenterpage(Centerpage):
    """Legacy view for centerpages built with the old cp-editor."""

    @zeit.web.reify
    def regions(self):
        regions = []

        if(len(self.area_solo.values()) > 0):
            region_fullwidth = LegacyRegion([self.area_solo])
            regions.append(region_fullwidth)

        region_multi = LegacyRegion([self.area_major, self.area_minor],
                                    kind='multi')
        regions.append(region_multi)

        regions += self.region_list_parquet

        return regions

    @zeit.web.reify
    def area_solo(self):
        """Return all fullwidth teaser blocks with a minimum length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) in (
                'zon-fullwidth')

        area = self.context.values()[0]['lead']
        return LegacyArea([m for m in area.itervalues() if valid_module(m)])

    @zeit.web.reify
    def area_major(self):
        """Return all non-fullwidth teaser blocks with a min length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) not in (
                'zon-fullwidth', 'hide')

        area = self.context.values()[0]['lead']
        return LegacyArea([m for m in area.itervalues() if valid_module(m)],
                          kind='major')

    @zeit.web.reify
    def area_minor(self):
        """Return an automated informatives-style area with buzz and ads."""

        return LegacyArea([m for m in (self.module_buzz_mostread,
                           self.module_printbox) if m], kind='minor')

    @zeit.web.reify
    def module_buzz_mostread(self):
        """Return buzz box module with the top 3 most read articles."""

        return zeit.content.cp.blocks.cpextra.CPExtraBlock(
            self.context,
            lxml.etree.fromstring('<container module="mostread"/>'))

    @zeit.web.reify
    def module_printbox(self):
        """Return the module block for the Printbox or Angebotsbox."""

        return zeit.content.cp.blocks.cpextra.CPExtraBlock(
            self.context,
            lxml.etree.fromstring('<container module="printbox"/>'))

    @zeit.web.reify
    def region_list_parquet(self):
        """Re-model the parquet to conform with new RAM-style structure."""

        regions = []
        for area in self.context.values()[1].itervalues():
            if area.kind != 'parquet':
                continue
            for block in area.values():
                try:
                    legacy = zope.component.getMultiAdapter(
                        (area, block),
                        zeit.content.cp.interfaces.IRenderedArea)
                except (zope.component.interfaces.ComponentLookupError,
                        AttributeError, TypeError):
                    continue
                regions.append(LegacyRegion([legacy], kind='parquet'))

        return regions
