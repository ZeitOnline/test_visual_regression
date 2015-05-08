# -*- coding: utf-8 -*-
import collections
import logging
import urllib
import uuid

import pyramid.response
import pyramid.view
import grokcore.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.layout

import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.sources
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.site.view
import zeit.web.site.spektrum

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.edit.interfaces.IBlock)
class LegacyModule(zeit.web.core.utils.nslist):

    def __init__(self, arg, **kw):
        super(LegacyModule, self).__init__([v for v in arg if v])
        self.layout = kw.pop('layout', 'default')
        self.type = 'teaser'

    @property
    def layout(self):
        return getattr(self, '_layout', None)

    @layout.setter
    def layout(self, value):
        self._layout = zeit.content.cp.layout.BlockLayout(
            value, value, areas=[], image_pattern=value)

    def __hash__(self):
        if getattr(self.layout, 'id', None):
            return hash((self.layout.id, id(self)))
        else:
            raise NotImplementedError()

    def __repr__(self):
        return object.__repr__(self)


@grokcore.component.implementer(zeit.content.cp.interfaces.IArea)
class LegacyArea(collections.OrderedDict):

    def __init__(self, arg, **kw):
        collections.OrderedDict.__init__(
            self, [('id-{}'.format(uuid.uuid1()), v) for v in arg if v])
        self.kind = kw.pop('kind', 'solo')
        self.is_teaserbar = kw.pop('is_teaserbar', False)

    def append(self, value):
        self['id-{}'.format(uuid.uuid1())] = value

    def __hash__(self):
        if self.kind:
            return hash((self.kind, id(self)))
        else:
            raise NotImplementedError()

    def __repr__(self):
        return object.__repr__(self)


@grokcore.component.implementer(zeit.content.cp.interfaces.IRegion)
class LegacyRegion(LegacyArea):

    def __init__(self, arg, **kw):
        collections.OrderedDict.__init__(
            self, [('id-{}'.format(uuid.uuid1()), v) for v in arg if v])
        self.kind = kw.pop('kind', 'solo')


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class Centerpage(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):
    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def regions(self):
        """List of regions, the outermost container making up our centerpage.
        :rtype: list
        """

        return self.context.values()

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

        if self.is_hp:
            return 'homepage'
        elif self.context.ressort:
            return self.context.ressort.lower()
        return ''

    def path_with_params(self, **kw):
        """Return the current request URL extended by given GET parameters."""
        params = dict(self.request.GET.items() + kw.items())
        return '?'.join([self.request.path_url, urllib.urlencode(params)])


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class LegacyCenterpage(Centerpage):
    """Legacy view for centerpages built with the old cp-editor."""

    @zeit.web.reify
    def regions(self):
        regions = []

        region_fullwidth = LegacyRegion([self.area_solo])
        regions.append(region_fullwidth)

        region_multi = LegacyRegion([self.area_major, self.area_minor],
                                    kind='multi')
        regions.append(region_multi)

        area_videostage = LegacyArea([self.module_videostage])
        region_video = LegacyRegion([area_videostage])
        regions.append(region_video)

        regions += self.region_list_parquet

        regions.append(self.region_snapshot)

        return regions

    @zeit.web.reify
    def area_solo(self):
        """Return all fullwidth teaser blocks with a minimum length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) in (
                'zon-fullwidth', None)

        area = self.context.values()[0]['lead']
        return LegacyArea([m for m in area.itervalues() if valid_module(m)])

    @zeit.web.reify
    def area_major(self):
        """Return all non-fullwidth teaser blocks with a min length of 1."""

        def valid_module(m):
            return zeit.web.core.template.get_layout(m) not in (
                'zon-fullwidth', None)

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

        module = LegacyModule(
            zeit.web.core.reach.fetch('mostread', self.ressort, limit=3),
            layout='buzz-mostread')
        module.header = 'Meistgelesene Artikel'
        return module

    @zeit.web.reify
    def module_buzz_comments(self):
        """Return buzz box module with the top 3 most commented articles."""

        module = LegacyModule(
            zeit.web.core.reach.fetch('comments', self.ressort, limit=3),
            layout='buzz-comments')
        module.header = 'Meistkommentiert'
        return module

    @zeit.web.reify
    def module_buzz_facebook(self):
        """Return buzz box module with the top 3 most shared articles."""

        module = LegacyModule(
            zeit.web.core.reach.fetch('facebook', self.ressort, limit=3),
            layout='buzz-facebook')
        module.header = 'Meistgeteilt'
        return module

    @zeit.web.reify
    def module_printbox(self):
        """Return the module block for the Printbox or Angebotsbox."""

        try:
            box = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/angebote/print-box')
        except TypeError:
            return

        module = LegacyModule([box], layout='printbox')
        module.has_digital_ad = False

        if box.byline == 'mo-mi':
            try:
                # Rewrite content with digital ad box
                box = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/angebote/angebotsbox')
                module.has_digital_ad = True
            except TypeError:
                pass

        try:
            box.image = zeit.content.image.interfaces.IImages(box).image
        except (AttributeError, TypeError):
            box.image = None

        return module

    @zeit.web.reify
    def module_videostage(self):
        """Return a video playlist module to be displayed on the homepage."""

        try:
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/video/playlist/36516804001')
        except TypeError:
            return

        module = LegacyModule([], layout='videostage')

        for index, video in enumerate(content.videos):
            layout = index and 'video-small' or 'video-large'
            module.append(LegacyModule([video], layout=layout))

        module.video_series_list = zeit.web.core.sources.video_series
        return module

    @zeit.web.reify
    def region_list_parquet(self):
        """Re-model the parquet to conform with new RAM-style structure."""

        regions = []

        for area in self.context.values()[1].itervalues():
            if area.kind != 'parquet':
                continue

            for block in area.values():
                if zeit.content.cp.interfaces.ICPExtraBlock.providedBy(block):
                    legacy = zeit.web.site.spektrum.HPFeed()
                elif zeit.content.cp.interfaces.ITeaserBlock.providedBy(block):
                    area.count = int(block.xml.get('display_amount', 3))
                    uid = unicode(block.xml.find('./referenced_cp'))
                    area.referenced_cp = zeit.cms.interfaces.ICMSContent(uid, None)
                    auto = zeit.content.cp.interfaces.IRenderedArea(area)
                    values = auto._query_centerpage()[:area.count]

                    lids = [block.layout.id] + area.count * ['zon-parquet-small']
                    modules = [LegacyModule([t], layout=lids.pop(0)) for t in values]
                    legacy = LegacyArea(modules, kind='parquet', is_teaserbar=True)

                    legacy.read_more = block.read_more
                    legacy.read_more_url = block.read_more_url
                    legacy.title = block.title
                    legacy.referenced_cp = area.referenced_cp
                else:
                    continue

                regions.append(LegacyRegion([legacy], kind='parquet'))

        return regions

    @zeit.web.reify
    def region_snapshot(self):
        """Return the centerpage snapshot region aka Momentaufnahme."""

        try:
            snapshot = zeit.web.core.interfaces.ITeaserImage(
                self.context.snapshot)
            assert snapshot
        except TypeError:
            snapshot = None

        module = LegacyModule([snapshot], layout='snapshot')
        return LegacyRegion([LegacyArea([module])])
