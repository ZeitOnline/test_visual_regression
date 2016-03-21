import logging

import grokcore.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss


log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='spektrum')
class ImageGroup(zeit.web.core.image.LocalImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.image_url
        self.uniqueId = u'http://xml.zeit.de/spektrum-image{}'.format(
            context.image_url.replace(u'http://www.spektrum.de', u''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='spektrum')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_area('spektrum')
class Spektrum(zeit.web.site.area.rss.RSSArea):

    feed_key = 'spektrum_hp_feed'
