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
        self.uniqueId = 'http://xml.zeit.de/spektrum-image{}'.format(
            context.image_url.replace('http://www.spektrum.de', ''))


@zeit.web.register_area('spektrum')
class Spektrum(zeit.web.site.area.rss.RSSArea):

    feed_key = 'spektrum_hp_feed'

    @zeit.web.reify
    def title(self):
        title = self.xml.findtext('title')
        if title and ': ' in title:
            return title.split(': ', 1)[1]
        return title

    @zeit.web.reify
    def supertitle(self):
        title = self.xml.findtext('title')
        if title and ': ' in title:
            return title.split(': ', 1)[0]
        return ''
