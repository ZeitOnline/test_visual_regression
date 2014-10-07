# -*- coding: utf-8 -*-
from pyramid.view import view_config

import zeit.content.cp.interfaces

import zeit.web.core.view
import zeit.web.site.view


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
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
                hasattr(x.layout, 'id') and x.layout.id and len(x) > 0),
            self.context['lead'].values())
        return [(i.layout.id, next(i.__iter__()), i) for i in blocks]

    @zeit.web.reify
    def area_buzz(self):
        # XXX: Mock buzzy article data.
        from zeit.cms.interfaces import ICMSContent as ic
        from zeit.web.core.utils import nslist

        area = nslist(ic('http://xml.zeit.de/artikel/0%s' % i)
                      for i in range(1, 4))
        area.layout = 'area_buzz_topread'
        return area

    @zeit.web.reify
    def topiclink_title(self):
        """Cache topiclink_title
        :rtype: string
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
