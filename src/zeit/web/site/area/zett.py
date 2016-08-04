import logging

import grokcore.component
import zope.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='zett')
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.image_url
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.uniqueId = u'http://xml.zeit.de/zett-image{}'.format(
            context.image_url.replace(conf.get('zett_img_host'), u''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='zett')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_area('zett')
class Zett(zeit.web.site.area.rss.RSSArea):

    feed_key = 'zett_hp_feed'
