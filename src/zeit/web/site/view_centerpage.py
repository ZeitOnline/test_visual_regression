# -*- coding: utf-8 -*-
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
        area_fullwidth = zeit.web.core.utils.nslist(
            self.area_fullwidth)
        area_fullwidth.layout = 'fullwidth'
        area_fullwidth.width = '1/1'

        region_fullwidth = zeit.web.core.utils.nslist(
            [area_fullwidth])
        region_fullwidth.layout = 'normal'

        area_main = zeit.web.core.utils.nslist(
            self.area_main)
        area_main.layout = 'lead'
        area_main.width = '2/3'

        area_informatives = zeit.web.core.utils.nslist(
            self.area_informatives)
        area_informatives.layout = 'informatives'
        area_informatives.width = '1/3'

        region_main = zeit.web.core.utils.nslist(
            [area_main, area_informatives])
        region_main.layout = 'normal'

        area_videomain = zeit.web.core.utils.nslist(
            self.area_videostage[:1])
        area_videomain.layout = 'video-stage-main'
        area_videomain.width = '2/3'

        area_videoplaylist = zeit.web.core.utils.nslist(
            self.area_videostage[1:4])
        area_videoplaylist.layout = 'video-stage-secondary'
        area_videoplaylist.width = '1/3'

        region_video = zeit.web.core.utils.nslist(
            [area_videomain, area_videoplaylist])
        region_video.layout = 'video'

        return [r for r in [region_fullwidth, region_main, region_video] if r]

    @zeit.web.reify
    def area_main(self):
        """Return all non-fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            return zeit.web.core.template.get_teaser_layout(b) not in (
                'zon-fullwidth', None)

        return [b for b in self.context['lead'].itervalues() if valid_block(b)]

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

        return [b for b in self.context['lead'].values() if valid_block(b)]

    @zeit.web.reify
    def area_informatives(self):
        return [b for b in [self.area_buzz_mostread,
                            self.area_buzz_facebook,
                            self.area_buzz_comments,
                            self.area_printbox] if b]

    @zeit.web.reify
    def area_buzz_mostread(self):
        """Return a pseudo teaser block with the top 3 most read articles.
        :rtype: zeit.web.core.utils.nslist
        """

        block = zeit.web.core.reach.fetch('mostread', self.ressort, limit=3)
        block.layout = zeit.web.core.utils.nsunicode('buzz-mostread')
        block.layout.id = zeit.web.core.utils.nsunicode('mostread')
        block.header = zeit.web.core.utils.nsunicode('Meistgelesene Artikel')
        return block

    @zeit.web.reify
    def area_buzz_comments(self):
        """Return a pseudo teaser block with the top 3 most commented articles.
        :rtype: zeit.web.core.utils.nslist
        """

        block = zeit.web.core.reach.fetch('comments', self.ressort, limit=3)
        block.layout = zeit.web.core.utils.nsunicode('buzz-comments')
        block.layout.id = zeit.web.core.utils.nsunicode('comments')
        block.header = zeit.web.core.utils.nsunicode('Meistkommentiert')
        return block

    @zeit.web.reify
    def area_buzz_facebook(self):
        """Return a pseudo teaser block with the top 3 most shared articles.
        :rtype: zeit.web.core.utils.nslist
        """

        block = zeit.web.core.reach.fetch('facebook', self.ressort, limit=3)
        block.layout = zeit.web.core.utils.nsunicode('buzz-facebook')
        block.layout.id = zeit.web.core.utils.nsunicode('facebook')
        block.header = zeit.web.core.utils.nsunicode('Meistgeteilt')
        return block

    @zeit.web.reify
    def area_printbox(self):
        """Return the content object for the Printbox or Angebotsbox.
        :rtype: dict
        """

        try:
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/angebote/print-box')
        except TypeError:
            return
        has_digital_ad = False

        if content.byline == 'mo-mi':
            try:
                # Rewrite content with digital ad box
                content = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/angebote/angebotsbox')
                has_digital_ad = True
            except TypeError:
                pass

        try:
            image = zeit.content.image.interfaces.IImages(content).image
        except (AttributeError, TypeError):
            image = None

        content.image = image
        content.has_digital_ad = has_digital_ad

        block = zeit.web.core.utils.nslist([content])
        block.layout = zeit.web.core.utils.nsunicode('printbox')
        block.layout.id = zeit.web.core.utils.nsunicode('printbox')
        return block

    @zeit.web.reify
    def area_videostage(self):
        """Return a video playlist object to be displayed on the homepage."""

        try:
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/video/playlist/36516804001')
        except TypeError:
            return

        blocks = []
        try:
            block = zeit.web.core.utils.nslist([content.videos[0]])
            block.layout = 'video-large'
            blocks.append(block)
        except IndexError:
            pass

        for video in content.videos[1:]:
            block = zeit.web.core.utils.nslist([video])
            block.layout = 'video-small'
            blocks.append(block)

        return blocks

    @zeit.web.reify
    def snapshot(self):
        """Return the centerpage snapshot aka `Momentaufnahme`.
        :rtype: zeit.content.image.image.RepositoryImage
        """

        try:
            snapshot = zeit.web.core.interfaces.ITeaserImage(
                self.context.snapshot)
        except TypeError:
            return

        block = zeit.web.core.utils.nslist([snapshot])
        block.layout = 'snapshot'
        return block

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
