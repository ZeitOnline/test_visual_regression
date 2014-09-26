# -*- coding: utf-8 -*-
import datetime

from pyramid.view import view_config

import zeit.content.cp.interfaces

import zeit.web.core.view


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view.Base):

    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def date_last_modified(self):
        """Timestamp representing the last update made to the centerpage.
        :rtype: datetime.datetime
        """

        # TODO: Implement actual timestamp.
        return datetime.datetime.now()

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
