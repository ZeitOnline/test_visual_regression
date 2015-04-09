# -*- coding: utf-8 -*-
import collections
import logging
import uuid

import pyramid.response
import pyramid.view

import zeit.cms.interfaces
import zeit.content.cp.interfaces

import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.sources
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.site.view

log = logging.getLogger(__name__)


class LegacyLayout(zeit.web.core.utils.nsunicode):
    def __new__(cls, arg):
        if isinstance(arg, tuple):
            arg, id_ = arg
        else:
            id_ = arg[:]
        layout = super(LegacyLayout, cls).__new__(cls, arg)
        layout.id = id_
        return layout

    def __repr__(self):
        return '<{} at {} with layout {}>'.format(
            self.__class__.__name__, hex(id(self)), unicode(self))


class LegacyModule(zeit.web.core.utils.nslist):
    def __init__(self, arg, **kw):
        super(LegacyModule, self).__init__(arg)
        self.layout = LegacyLayout(kw.pop('layout', 'default'))

    def __repr__(self):
        return '<{} at {} with {} entr{}>'.format(
            self.__class__.__name__, hex(id(self)), len(self),
            'y' if len(self) == 1 else 'ies')


class LegacyArea(collections.OrderedDict):
    def __init__(self, arg, **kw):
        super(LegacyArea, self).__init__(
            [('id-{}'.format(uuid.uuid1()), v) for v in arg])
        self.layout = LegacyLayout(kw.pop('layout', 'fullwidth'))
        self.width = kw.pop('width', '1/1')

    def __repr__(self):
        return '<{} at {} with {} module{}>'.format(
            self.__class__.__name__, hex(id(self)), len(self),
            '' if len(self) == 1 else 's')


class LegacyRegion(collections.OrderedDict):
    def __init__(self, arg, **kw):
        super(LegacyRegion, self).__init__(
            [('id-{}'.format(uuid.uuid1()), v) for v in arg])
        self.layout = LegacyLayout(kw.pop('layout', 'normal'))
        self.title = kw.pop('title', None)

    def __repr__(self):
        return '<{} at {} with {} area{}>'.format(
            self.__class__.__name__, hex(id(self)), len(self),
            '' if len(self) == 1 else 's')


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class LegacyCenterpage(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):

    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def regions(self):
        regions = []

        region_fullwidth = LegacyRegion([self.area_fullwidth],
                                        layout='fullwidth')
        regions.append(region_fullwidth)

        region_lead = LegacyRegion([self.area_main, self.area_informatives],
                                   layout='lead')
        regions.append(region_lead)

        area_videostage = LegacyArea([self.module_videostage],
                                     layout='video',
                                     width='1/1')
        region_video = LegacyRegion([area_videostage],
                                    layout='fullwidth')
        regions.append(region_video)

        regions += self.region_list_parquet

        regions.append(self.region_snapshot)

        return regions

    @zeit.web.reify
    def region_snapshot(self):
        area_snapshot = LegacyArea([b for b in [self.module_snapshot] if b],
                                   layout='snapshot', width='1/1')

        return LegacyRegion([area_snapshot], layout='snapshot')

    @zeit.web.reify
    def area_main(self):
        """Return all non-fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_module(m):
            return zeit.web.core.template.get_teaser_layout(m) not in (
                'zon-fullwidth', None)

        area = self.context.values()[0]['lead']
        return LegacyArea(
            [m for m in area.itervalues() if valid_module(m)],
            layout='lead', width='2/3')

    @zeit.web.reify
    def region_list_parquet(self):
        def valid_area(a):
            try:
                return a.layout.id in ('parquet',)
            except AttributeError:
                return

        def valid_module(m):
            return zeit.web.core.template.get_teaser_layout(m) in (
                'zon-parquet-large', 'zon-parquet-small') or getattr(
                m, 'cpextra', None) in ('parquet-spektrum',)

        def get_layout(m):
            try:
                return getattr(m, 'cpextra', None) or m.layout.id
            except AttributeError:
                return 'parquet-regular'

        return [LegacyRegion([LegacyArea([m], layout=get_layout(m))]) for area
                in self.context.values()[1].itervalues() if valid_area(area)
                for m in area.itervalues() if valid_module(m)]

    @zeit.web.reify
    def area_fullwidth(self):
        """Return all fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_module(m):
            return zeit.web.core.template.get_teaser_layout(m) in (
                'zon-fullwidth',)

        lead = self.context.values()[0]['lead']
        return LegacyArea(
            [m for m in lead.itervalues() if valid_module(m)])

    @zeit.web.reify
    def area_informatives(self):
        return LegacyArea([m for m in (
            self.module_buzz_mostread, self.module_printbox) if m],
            layout='informatives', width='1/3')

    @zeit.web.reify
    def module_buzz_mostread(self):
        """Return a pseudo teaser block with the top 3 most read articles.
        :rtype: LegacyModule
        """

        module = LegacyModule(
            zeit.web.core.reach.fetch('mostread', self.ressort, limit=3),
            layout=('buzz-mostread', 'mostread'))
        module.header = 'Meistgelesene Artikel'
        return module

    @zeit.web.reify
    def module_buzz_comments(self):
        """Return a pseudo teaser block with the top 3 most commented articles.
        :rtype: LegacyModule
        """

        module = LegacyModule(
            zeit.web.core.reach.fetch('comments', self.ressort, limit=3),
            layout=('buzz-comments', 'comments'))
        module.header = 'Meistkommentiert'
        return module

    @zeit.web.reify
    def module_buzz_facebook(self):
        """Return a pseudo teaser block with the top 3 most shared articles.
        :rtype: LegacyModule
        """

        module = LegacyModule(
            zeit.web.core.reach.fetch('facebook', self.ressort, limit=3),
            layout=('buzz-facebook', 'facebook'))
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

        has_digital_ad = False
        if box.byline == 'mo-mi':
            try:
                # Rewrite content with digital ad box
                box = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/angebote/angebotsbox')
                has_digital_ad = True
            except TypeError:
                pass

        try:
            box.image = zeit.content.image.interfaces.IImages(box).image
        except (AttributeError, TypeError):
            box.image = None

        module = LegacyModule([box], layout='printbox')
        module.has_digital_ad = has_digital_ad
        return module

    @zeit.web.reify
    def module_videostage(self):
        """Return a video playlist object to be displayed on the homepage."""

        try:
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/video/playlist/36516804001')
        except TypeError:
            return

        module = LegacyModule([], layout='videostage')

        for index, video in enumerate(content.videos):
            layout = index and 'video-small' or 'video-large'
            module.append(LegacyModule([video], layout=layout))

        return module

    @zeit.web.reify
    def module_snapshot(self):
        """Return the centerpage snapshot aka `Momentaufnahme`.
        :rtype: zeit.content.image.image.RepositoryImage
        """

        try:
            snapshot = zeit.web.core.interfaces.ITeaserImage(
                self.context.snapshot)
            return LegacyModule([snapshot], layout='snapshot')
        except TypeError:
            return

    @zeit.web.reify
    def last_semantic_change(self):
        """Timestamp representing the last semantic change of the centerpage.
        :rtype: datetime.datetime
        """

        return zeit.cms.content.interfaces.ISemanticChange(
            self.context).last_semantic_change

    @zeit.web.reify
    def topiclink_title(self):
        """Cache topiclink_title
        :rtype: str
        """

        return self.context.topiclink_title or 'Schwerpunkte'

    @zeit.web.reify
    def topiclinks(self):
        return zeit.web.core.interfaces.ITopicLink(self.context)

    @zeit.web.reify
    def spektrum_hp_feed(self):
        try:
            return zeit.web.site.spektrum.HPFeed()
        except (TypeError, AttributeError):
            return

    @zeit.web.reify
    def video_series_list(self):
        return zeit.web.core.sources.video_series

    @zeit.web.reify
    def ressort(self):
        if self.is_hp:
            return 'homepage'
        elif self.context.ressort:
            return self.context.ressort.lower()
        else:
            return ''


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class Centerpage(LegacyCenterpage):

    @zeit.web.reify
    def regions(self):
        return self.context.values()
