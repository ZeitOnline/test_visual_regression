# -*- coding: utf-8 -*-
import collections
import logging

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
    def __init__(self, arg, **kw):
        if isinstance(arg, basestring):
            layout, self.id = arg, None
        else:
            layout, self.id = arg
        super(LegacyLayout, self).__init__(layout, **kw)


class LegacyModule(zeit.web.core.utils.nslist):
    def __init__(self, arg, **kw):
        super(LegacyModule, self).__init__(arg)
        self.layout = LegacyLayout(kw.pop('layout', 'default'))


class LegacyArea(zeit.web.core.utils.nslist):
    def __init__(self, arg, **kw):
        super(LegacyArea, self).__init__(arg)
        self.layout = LegacyLayout(kw.pop('layout', 'fullwidth'))
        self.width = kw.pop('width', '1/1')


class LegacyRegion(collections.OrderedDict):
    def __init__(self, arg, **kw):
        super(LegacyRegion, self).__init__(arg)
        self.layout = LegacyLayout(kw.pop('layout', 'normal'))
        self.title = kw.pop('title', None)

    def __iter__(self):
        return iter(self[k] for k in super(LegacyRegion, self).__iter__())


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class LegacyCenterpage(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):

    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def last_semantic_change(self):
        """Timestamp representing the last semantic change of the centerpage.
        :rtype: datetime.datetime
        """

        return zeit.cms.content.interfaces.ISemanticChange(
            self.context).last_semantic_change

    @zeit.web.reify
    def regions(self):
        regions = []

        region_fullwidth = LegacyRegion([('fullwidth', self.area_fullwidth)],
                                        layout='fullwidth')
        regions.append(region_fullwidth)

        region_lead = LegacyRegion([('main', self.area_main),
                                    ('informatives', self.area_informatives)],
                                   layout='lead')
        regions.append(region_lead)

        area_video_main = LegacyArea(self.area_videostage[:1],
                                     layout='video-stage-main',
                                     width='2/3')

        area_video_secondary = LegacyArea(self.area_videostage[1:4],
                                          layout='video-stage-secondary',
                                          width='1/3')

        region_video = LegacyRegion([('main', area_video_main),
                                     ('secondary', area_video_secondary)],
                                    layout='video')
        regions.append(region_video)

        area_snapshot = LegacyArea([b for b in [self.snapshot] if b],
                                   layout='snapshot', width='1/1')

        region_snapshot = LegacyRegion([('main', area_snapshot)],
                                       layout='snapshot')
        regions.append(region_snapshot)

        return regions

    @zeit.web.reify
    def area_main(self):
        """Return all non-fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            return zeit.web.core.template.get_teaser_layout(b) not in (
                'zon-fullwidth', None)

        return LegacyArea(
            [b for b in self.context['lead'].itervalues() if valid_block(b)],
            layout='lead', width='2/3')

    @zeit.web.reify
    def area_parquet(self):
        def valid_bar(b):
            try:
                return b.layout.id in ('parquet',)
            except AttributeError:
                return

        def valid_block(b):
            return zeit.web.core.template.get_teaser_layout(b) in (
                'zon-parquet-large', 'zon-parquet-small') or getattr(
                b, 'cpextra', None) in ('parquet-spektrum',)

        return [b for bar in self.context['teaser-mosaic'].itervalues() if
                valid_bar(bar) for b in bar.itervalues() if valid_block(b)]

    @zeit.web.reify
    def area_fullwidth(self):
        """Return all fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            return zeit.web.core.template.get_teaser_layout(b) in (
                'zon-fullwidth',)

        return LegacyArea(
            [b for b in self.context['lead'].values() if valid_block(b)])

    @zeit.web.reify
    def area_informatives(self):
        return LegacyArea([b for b in (
            self.module_buzz_comments, self.module_buzz_facebook,
            self.module_buzz_mostread, self.module_printbox) if b][-2:],
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

        module = LegacyModule([box], layout=('printbox', 'printbox'))
        module.has_digital_ad = has_digital_ad
        return module

    @zeit.web.reify
    def area_videostage(self):
        """Return a video playlist object to be displayed on the homepage."""

        try:
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/video/playlist/36516804001')
        except TypeError:
            return

        modules = []
        try:
            module = LegacyModule([content.videos[0]], layout='video-large')
            modules.append(module)
        except IndexError:
            pass

        for video in content.videos[1:]:
            module = LegacyModule([video], layout='video-small')
            modules.append(module)

        return modules

    @zeit.web.reify
    def snapshot(self):
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
        return []
