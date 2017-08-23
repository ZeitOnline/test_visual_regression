from collections import namedtuple

import grokcore.component
import logging
import zope.component


import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.area.rss
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.web.site.area.rss.IRSSLink, name='jobbox')
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    @zeit.web.reify
    def uniqueId(self):
        return 'http://xml.zeit.de/academics-image{}'.format(
            self.image_url.replace('https://www.academics.de', ''))


@grokcore.component.implementer(zeit.web.site.area.rss.IRSSLink)
@grokcore.component.adapter(None, name='jobbox')
class Link(zeit.web.site.area.rss.RSSLink):

    pass


@zeit.web.register_module('jobbox')
class Jobbox(zeit.web.core.centerpage.Module, list):

    def __init__(self, context):
        # BW-Compat for old Jobboxes which are cp-extras and dont have a jobbox
        # object associated with the CP-Extra module
        try:
            self.source_obj = context.jobbox
        except AttributeError:
            # BW-Compat for old Jobboxes which are cp-extras and dont have a jobbox
            # object associated with the CP-Extra block
            # Create a named-Tuple as a fallback
            conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
            JobboxSourceObject = namedtuple('Jobbox', ['feed_url', 'teaser',
                                           'landing_url'])
            self.source_obj = JobboxSourceObject(
                feed_url=conf.get('academics_hp_feed'),
                teaser="Aktuelle Jobs im ZEIT Stellenmarkt",
                landing_url="http://jobs.zeit.de/"
            )
        list.__init__(self, zeit.web.site.area.rss.parse_feed(
            self.source_obj.feed_url, 'jobbox'))
        zeit.web.core.centerpage.Module.__init__(self, context)

    @zeit.web.reify
    def teaser_text(self):
        return self.source_obj.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.source_obj.landing_url
