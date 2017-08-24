
import grokcore.component
import logging

import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink,
                            name='jobbox_ticker')
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    @zeit.web.reify
    def uniqueId(self):
        return 'http://xml.zeit.de/academics-image{}'.format(
            self.image_url.replace('https://www.academics.de', ''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='jobbox_ticker')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_module('jobbox_ticker')
class JobboxTicker(zeit.web.core.centerpage.Module, list):

    def __init__(self, context):
        self.source_obj = context.jobbox_ticker
        list.__init__(self, zeit.web.site.area.rss.parse_feed(
        self.source_obj.feed_url, 'jobbox_ticker'))
        zeit.web.core.centerpage.Module.__init__(self, context)

    @zeit.web.reify
    def teaser_text(self):
        return self.source_obj.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.source_obj.landing_url
