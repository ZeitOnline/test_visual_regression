import logging

import grokcore.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.site.area.rss

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.RSSLink, name='zett')
class ZettImageGroup(zeit.web.core.centerpage.LocalImageGroup):

    def __init__(self, context):
        super(ZettImageGroup, self).__init__(context)
        self.image_url = context.image_url
        self.uniqueId = 'http://xml.zeit.de/zett-image{}'.format(
            context.image_url.replace('http://ze.tt', ''))


@zeit.web.register_area('zett')
class Zett(zeit.web.site.area.rss.RSSArea):

    feed_key = 'zett_hp_feed'
    module_layout = 'zon-small'
    # XXX Don't split title and supertitle
