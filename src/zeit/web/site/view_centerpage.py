# -*- coding: utf-8 -*-
import logging

import pyramid.response
import pyramid.view

import zeit.cms.interfaces
import zeit.content.cp.interfaces

import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.site.video_series
import zeit.web.site.view

log = logging.getLogger(__name__)


def known_content(res):
    return (zeit.content.article.interfaces.IArticle.providedBy(res[1]) or
            zeit.content.gallery.interfaces.IGallery.providedBy(res[1]) or
            zeit.content.video.interfaces.IVideo.providedBy(res[1]))


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    renderer='templates/centerpage.html')
class Centerpage(
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
    def area_main(self):
        """Return all non-fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            try:
                return len(b) and b.layout.id and (
                    zeit.web.core.template.get_mapped_teaser(b.layout.id)
                    not in ('zon-fullwidth',))
            except (TypeError, AttributeError):
                return

        return [(b.layout.id, iter(b).next(), b) for b in
                self.context['lead'].values() if valid_block(b)]

    @zeit.web.reify
    def area_parquet(self):
        def valid_bar(b):
            try:
                return b.layout.id in ('parquet',)
            except AttributeError:
                return

        def valid_blocks(b):
            try:
                return b.layout.id in ('parquet-large', 'parquet-regular')
            except AttributeError:
                try:
                    return b.cpextra in ('parquet-spektrum')
                except AttributeError:
                    return

        teaser_bars = filter(valid_bar, self.context['teaser-mosaic'].values())
        teaser_bar_blocks = sum([bar.values() for bar in teaser_bars], [])
        parquet_teaser_blocks = filter(valid_blocks, teaser_bar_blocks)
        return parquet_teaser_blocks

    @zeit.web.reify
    def area_fullwidth(self):
        """Return all fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            try:
                return len(b) and b.layout.id and (
                    zeit.web.core.template.get_mapped_teaser(b.layout.id) in (
                        'zon-fullwidth',))
            except (TypeError, AttributeError):
                return

        return [(b.layout.id, iter(b).next(), b) for b in
                self.context['lead'].values() if valid_block(b)]

    @zeit.web.reify
    def area_buzz_mostread(self):
        """Return a pseudo teaser block with the top 3 most read articles.
        :rtype: zeit.web.core.utils.nslist
        """

        area = zeit.web.core.reach.fetch('mostread', self.ressort, limit=3)
        area.layout = zeit.web.core.utils.nsunicode('buzz-mostread')
        area.layout.id = zeit.web.core.utils.nsunicode('mostread')
        area.header = zeit.web.core.utils.nsunicode('Meistgelesene Artikel')
        return area

    @zeit.web.reify
    def area_buzz_comments(self):
        """Return a pseudo teaser block with the top 3 most commented articles.
        :rtype: zeit.web.core.utils.nslist
        """

        area = zeit.web.core.reach.fetch('comments', self.ressort, limit=3)
        area.layout = zeit.web.core.utils.nsunicode('buzz-comments')
        area.layout.id = zeit.web.core.utils.nsunicode('comments')
        area.header = zeit.web.core.utils.nsunicode('Meistkommentiert')
        return area

    @zeit.web.reify
    def area_buzz_facebook(self):
        """Return a pseudo teaser block with the top 3 most shared articles.
        :rtype: zeit.web.core.utils.nslist
        """

        area = zeit.web.core.reach.fetch('facebook', self.ressort, limit=3)
        area.layout = zeit.web.core.utils.nsunicode('buzz-facebook')
        area.layout.id = zeit.web.core.utils.nsunicode('facebook')
        area.header = zeit.web.core.utils.nsunicode('Meistgeteilt')
        return area

    @zeit.web.reify
    def area_printbox(self):
        """Return the content object for the Printbox or Angebotsbox.
        :rtype: dict
        """

        uri = 'http://xml.zeit.de/angebote/print-box'
        content = zeit.cms.interfaces.ICMSContent(uri)
        has_digital_ad = False

        if content.byline == 'mo-mi':
            # Rewrite content with digital ad box
            uri = 'http://xml.zeit.de/angebote/angebotsbox'
            content = zeit.cms.interfaces.ICMSContent(uri)
            has_digital_ad = True

        printbox = content
        printbox.has_digital_ad = has_digital_ad
        printbox.image = zeit.content.image.interfaces.IImages(content).image
        return printbox

    @zeit.web.reify
    def area_videobar(self):
        """Return a video playlist object to be displayed on the homepage."""
        unique_id = 'http://xml.zeit.de/video/playlist/36516804001'
        return zeit.cms.interfaces.ICMSContent(unique_id)

    @zeit.web.reify
    def snapshot(self):
        """Return the centerpage snapshot aka `Momentaufnahme`.
        :rtype: zeit.content.image.image.RepositoryImage
        """
        snapshot = self.context.snapshot
        return zeit.web.core.interfaces.ITeaserImage(snapshot) if (
            snapshot is not None) else None

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
        return zeit.web.site.video_series.video_series
