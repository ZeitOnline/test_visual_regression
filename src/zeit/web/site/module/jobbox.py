import grokcore.component
import logging
import zope.component

import zeit.content.image.interfaces

import zeit.web.core.image
import zeit.web.site.area.rss
import zeit.web.site.module


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
class Jobbox(zeit.web.site.module.Module, list):

    def __init__(self, context):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('academics_hp_feed')

        # TODO: Delete this line once corresponding varnish PR is merged!
        #       https://github.com/ZeitOnline/zeit.varnish/pull/94
        url = 'http://jobs.zeit.de/stellenangebote/adpanel_333644.html?format=rss_2.0'  # NOQA

        list.__init__(self, zeit.web.site.area.rss.parse_feed(url, 'jobbox'))
        zeit.web.site.module.Module.__init__(self, context)
        self.title = "klaus"
