# -*- coding: utf-8 -*-
import collections
import logging
import uuid

import grokcore.component
import pyramid.response
import pyramid.view
import zope.component
import zope.component.interfaces
import zope.interface

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces
import zeit.content.cp.layout

import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.site.area.spektrum
import zeit.web.site.module
import zeit.web.site.module.buzzbox
import zeit.web.site.module.printbox
import zeit.web.site.view


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.edit.interfaces.IBlock)
class LegacyModule(zeit.web.site.module.Module, zeit.web.core.utils.nslist):

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
        self.automatic = kw.pop('kind', False)
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
        area._v_try_to_retrieve_content = True
        area._v_retrieved_content = 0
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
    def canonical_url(self):
        return self.request.url

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
                nav_item = zeit.web.core.navigation.navigation_by_name[
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
    def regions(self):
        region_list = super(Centerpage, self).regions
        if self.is_hp:
            region_list.append(self.region_snapshot)
        return region_list

    @zeit.web.reify
    def last_semantic_change(self):
        """Timestamp representing the last semantic change of the centerpage.
        :rtype: datetime.datetime
        """

        return zeit.cms.content.interfaces.ISemanticChange(
            self.context).last_semantic_change

    @zeit.web.reify
    def topic_links(self):
        """Return topic links of a centerpage as a TopicLink object
        :rtype: zeit.web.core.centerpage.TopicLink
        """

        return zeit.web.core.interfaces.ITopicLink(self.context)

    @zeit.web.reify
    def ressort(self):
        """Ressort of the centerpage or the string `homepage` if context is HP.
        :rtype: str
        """

        if self.context.type == 'homepage':
            return 'homepage'
        elif self.context.ressort:
            return self.context.ressort.lower()
        return ''

    @zeit.web.reify
    def region_snapshot(self):
        """Return the centerpage snapshot region aka Momentaufnahme."""
        # TODO: Reimplement snapshot as a proper vivi+friedbert module.
        try:
            snapshot = zeit.web.core.interfaces.ITeaserImage(
                self.context.snapshot)
            assert snapshot
        except TypeError:
            snapshot = None

        module = LegacyModule([snapshot], layout='snapshot')
        return LegacyRegion([LegacyArea([module])])


@pyramid.view.view_config(
    name='area',
    context=zeit.content.cp.interfaces.ICP2015,
    renderer='templates/inc/area/includer.html')
class CenterpageArea(Centerpage):

    def __init__(self, context, request):
        if not request.subpath:
            raise pyramid.httpexceptions.NotFound()

        self.context = None
        self.request = request

        for region in context.values():
            for area in region.values():
                if area.uniqueId.rsplit('/', 1)[-1] == request.subpath[-1]:
                    self.context = zeit.web.core.centerpage.get_area(area)
                    return

    def __call__(self):
        return {
            'area': self.context,
            'region_loop': {'index': 1}
        }


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.IStoryStream,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/storystream.html')
class Storystream(
        Centerpage):
    """Main view class for ZEIT ONLINE storystreams."""
    pass


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

        regions.append(self.region_snapshot)

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

        return zeit.web.site.module.buzzbox.MostreadBuzzbox(self.context)

    @zeit.web.reify
    def module_printbox(self):
        """Return the module block for the Printbox or Angebotsbox."""

        return zeit.web.site.module.printbox.Printbox(self.context)

    @zeit.web.reify
    def region_list_parquet(self):
        """Re-model the parquet to conform with new RAM-style structure."""

        regions = []
        for area in self.context.values()[1].itervalues():
            if area.kind != 'parquet':
                continue
            for block in area.values():
                if zeit.content.cp.interfaces.ICPExtraBlock.providedBy(block):
                    if block.cpextra != 'parquet-spektrum':
                        continue
                    legacy = zeit.web.site.area.spektrum.HPFeed()
                else:
                    try:
                        legacy = zope.component.getMultiAdapter(
                            (area, block),
                            zeit.content.cp.interfaces.IRenderedArea)
                    except (zope.component.interfaces.ComponentLookupError,
                            AttributeError, TypeError):
                        continue
                regions.append(LegacyRegion([legacy], kind='parquet'))

        return regions
