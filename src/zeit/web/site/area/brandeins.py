import logging

import grokcore.component
import zope.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='brandeins')
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    @zeit.web.reify
    def uniqueId(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return u'http://xml.zeit.de/zett-image{}'.format(
            self.image_url.replace(conf.get('zett_img_host'), u''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='brandeins')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_area('brandeins')
class Brandeins(zeit.web.site.area.rss.RSSArea):

    feed_key = 'zett_hp_feed'
