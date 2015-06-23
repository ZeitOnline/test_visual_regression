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

    def __iter__(self):
        for region in self.context.values():
            for area in region.values():
                for block in area.values():
                    if not hasattr(block, '__iter__'):
                        continue
                    for teaser in block:
                        if zeit.web.core.view.known_content(teaser):
                            yield teaser

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'homepage'

    @zeit.web.reify
    def has_solo_leader(self):
        try:
            return self.regions[0].values()[0].kind == 'solo'
        except (AttributeError, IndexError):
            return False

    @zeit.web.reify
    def tracking_type(self):
        return type(self.context).__name__.title()

    @zeit.web.reify
    def comment_counts(self):
        return zeit.web.core.comments.get_counts(*[t.uniqueId for t in self])


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             name='json_update_time',
             renderer='jsonp')
class JsonUpdateTimeView(zeit.web.core.view.Base):

    def __call__(self):
        return {'last_published': self.last_published(),
                'last_published_semantic': self.last_published_semantic()}

    def last_published(self):
        date = self.publish_info.date_last_published
        try:
            return date.isoformat()
        except AttributeError:
            return ''

    def last_published_semantic(self):
        date = self.publish_info.date_last_published_semantic
        try:
            return date.isoformat()
        except AttributeError:
            return ''


def get_last_published_semantic(context):
    return zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published_semantic
