# -*- coding: utf-8 -*-
from pyramid.view import view_config

import zeit.cms.interfaces
import zeit.cms.workflow
import zeit.content.cp.interfaces

import zeit.web.core.view


class Centerpage(zeit.web.core.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Centerpage, self).__init__(*args, **kwargs)
        self._copyrights = {}
        self.context.advertising_enabled = self.banner_on

        # Most of our resources will be purged from now on. We test this new
        # mechanism on CPs. This might be valid for all resources in the future
        # (RD, 7.8.2015)
        self.request.response.headers.add('s-maxage', '21600')

    def __iter__(self):
        for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                self.context):
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


@view_config(route_name='json_update_time',
             renderer='jsonp')
def json_update_time(request):
    try:
        resource = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/{}'.format(request.matchdict['path']))
        info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        dlps = info.date_last_published_semantic.isoformat()
        dlp = info.date_last_published.isoformat()
    except (AttributeError, KeyError, TypeError):
        dlps = dlp = None
    return {'last_published': dlp, 'last_published_semantic': dlps}
