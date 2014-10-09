# -*- coding: utf-8 -*-

from pyramid.view import view_config

import zeit.content.cp.interfaces

import zeit.web.core.view


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view.Base):

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
        """Filter teaser with layout from teaser list.
        :rtype: dict
        """
        blocks = filter(
            lambda x: hasattr(x, 'layout') and x.layout and (
                hasattr(x.layout, 'id') and x.layout.id and len(x) > 0
                and x.layout.id != 'zon-fullwidth'),
            self.context['lead'].values())
        return [(i.layout.id, next(i.__iter__()), i) for i in blocks]

    @zeit.web.reify
    def area_fullwidth(self):
        for teaser_block in self.context['lead'].values():
            try:
                if 'zon-fullwidth' in teaser_block.layout.id:
                    return [(teaser_block.layout.id, next(teaser_block.__iter__()), teaser_block)]
            except AttributeError:
                continue
        return []

    @zeit.web.reify
    def topiclink_title(self):
        """Cache topiclink_title
        : rtype: string
        """
        return self.context.topiclink_title if (
            self.context.topiclink_title is not None) else 'Schwerpunkte'

    @zeit.web.reify
    def topiclinks(self):
        """Filter and restructure all topiclinks and labels
        : rtype: dict
        """
        link_list = []
        for i in xrange(1, 4):
            label = getattr(self.context, 'topiclink_label_%s' % i, None)
            link = getattr(self.context, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                link_list.append((label, link))
        return link_list
