# -*- coding: utf-8 -*-
from pyramid.view import view_config

import zeit.content.cp.interfaces

import zeit.web.core.view


class Centerpage(zeit.web.core.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self._copyrights = {}
        self.context.advertising_enabled = self.banner_on

    @zeit.web.reify
    def is_hp(self):
        return self.request.path == '/' + self.request.registry.settings.hp

    @zeit.web.reify
    def meta_robots(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        try:
            if seo.meta_robots:
                return seo.meta_robots
        except AttributeError:
            pass
        return 'index,follow,noodp,noydir,noarchive'

    @zeit.web.reify
    def tracking_type(self):
        return type(self.context).__name__.title()


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             name='json_update_time',
             renderer='jsonp')
class JsonUpdateTimeView(zeit.web.core.view.Base):

    def __call__(self):
        return {'last_published': self.last_published()}

    def last_published(self):
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_last_published
        try:
            return date.isoformat()
        except AttributeError:
            return ''
