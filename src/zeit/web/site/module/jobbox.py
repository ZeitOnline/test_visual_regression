import grokcore.component
import logging
import zope.component

import zeit.content.image.interfaces

import zeit.web.core.image
import zeit.web.site.area.rss
import zeit.web.core.module


log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='jobbox')
class ImageGroup(zeit.web.core.image.LocalImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.image_url
        self.uniqueId = 'http://xml.zeit.de/academics-image{}'.format(
            context.image_url.replace('https://www.academics.de', ''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='jobbox')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_module('jobbox')
class Jobbox(zeit.web.core.module.Module, list):

    def __init__(self, context):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('academics_hp_feed')
        list.__init__(self, zeit.web.site.area.rss.parse_feed(url, 'jobbox'))
        zeit.web.core.module.Module.__init__(self, context)
        self.title = "klaus"
