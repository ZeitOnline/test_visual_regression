import logging

import grokcore.component

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.site.area.rss


log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.RSSLink, name='spektrum')
class ImageGroup(zeit.web.core.centerpage.LocalImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.image_url
        self.uniqueId = 'http://xml.zeit.de/spektrum-image{}'.format(
            context.image_url.replace('http://www.spektrum.de', ''))


@zeit.web.register_area('spektrum')
class Spektrum(zeit.web.site.area.rss.RSSArea):

    feed_key = 'spektrum_hp_feed'
    module_layout = 'zon-small'
