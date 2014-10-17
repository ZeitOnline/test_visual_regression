# -*- coding: utf-8 -*-
import pyramid.response
import pyramid.view

import zeit.content.cp.interfaces

import zeit.web.core.reach
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.site.view


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
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
                hasattr(x.layout, 'id') and x.layout.id and len(x) > 0
                and x.layout.id != 'zon-fullwidth'
                and x.layout.id != 'zon-fullwidth-onimage'),
            self.context['lead'].values())
        return [(i.layout.id, iter(i).next(), i) for i in blocks]

    @zeit.web.reify
    def area_fullwidth(self):
        for teaser_block in self.context['lead'].values():
            try:
                if (('zon-fullwidth' in teaser_block.layout.id) or
                        ('zon-fullwidth-onimage' in teaser_block.layout.id)):
                    return [(teaser_block.layout.id, iter(teaser_block).next(),
                            teaser_block)]
            except AttributeError:
                continue
        return []

    @zeit.web.reify
    def area_buzz_mostread(self):
        area = zeit.web.core.reach.fetch('mostread', self.ressort, limit=3)
        area.layout = zeit.web.core.utils.nsunicode('buzz-mostread')
        area.layout.id = zeit.web.core.utils.nsunicode('mostread')
        area.header = zeit.web.core.utils.nsunicode('Meistgelesen')
        return area

    @zeit.web.reify
    def area_buzz_facebook(self):
        area = zeit.web.core.reach.fetch('facebook', self.ressort, limit=3)
        area.layout = zeit.web.core.utils.nsunicode('buzz-facebook')
        area.layout.id = zeit.web.core.utils.nsunicode('facebook')
        area.header = zeit.web.core.utils.nsunicode('Meistempfohlen')
        return area

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
