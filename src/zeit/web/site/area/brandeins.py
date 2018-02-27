import logging

import urllib
import urlparse

import grokcore.component

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
        parts = urlparse.urlparse(self.image_url)
        return u'http://xml.zeit.de/brandeins-image{}{}'.format(
            parts.path, urllib.quote_plus('?' + parts.query))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='brandeins')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_area('brandeins')
class Brandeins(zeit.web.site.area.rss.RSSArea):

    feed_key = 'brandeins_hp_feed'
