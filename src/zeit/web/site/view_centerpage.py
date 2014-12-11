# -*- coding: utf-8 -*-
import pyramid.response
import pyramid.view
import logging

import zeit.content.cp.interfaces

import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
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
                return len(b) and b.layout.id and \
                    zeit.web.core.template.get_mapped_teaser(b.layout.id) \
                    not in ('zon-fullwidth',)
            except (TypeError, AttributeError):
                return

        return [(b.layout.id, iter(b).next(), b) for b in
                self.context['lead'].values() if valid_block(b)]

    @zeit.web.reify
    def area_fullwidth(self):
        """Return all fullwidth teaser blocks with a minimum length of 1.
        :rtype: list
        """

        def valid_block(b):
            try:
                return len(b) and b.layout.id and \
                    zeit.web.core.template.get_mapped_teaser(b.layout.id) in (
                        'zon-fullwidth',)
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
        """Filter and restructure all topiclinks and labels
        :rtype: dict
        """

        link_list = []
        for i in xrange(1, 4):
            label = getattr(self.context, 'topiclink_label_%s' % i, None)
            link = getattr(self.context, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                link_list.append((label, link))
        return link_list
