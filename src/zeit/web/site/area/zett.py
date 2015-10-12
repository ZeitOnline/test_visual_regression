import logging

import grokcore.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='zett')
class ImageGroup(zeit.web.core.image.LocalImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.image_url
        self.uniqueId = 'http://xml.zeit.de/zett-image{}'.format(
            context.image_url.replace('http://ze.tt', ''))


@zeit.web.register_area('zett')
class Zett(zeit.web.site.area.rss.RSSArea):

    feed_key = 'zett_hp_feed'
