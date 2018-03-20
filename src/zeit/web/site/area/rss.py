import email
import logging

import grokcore.component
import lxml.etree
import requests
import zope.component
import zope.interface

import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.content.image.interfaces
import zeit.content.link.interfaces

import zeit.web
import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.centerpage
import zeit.web.core.metrics


log = logging.getLogger(__name__)
SHORT_TERM_CACHE = zeit.web.core.cache.get_region('short_term')


class IRSSLink(zeit.content.link.interfaces.ILink):

    image_url = zope.interface.Attribute('image_url')


class RSSLink(object):

    zope.interface.implements(IRSSLink)

    def __init__(self, xml):
        self.xml = xml
        self.__name__ = None
        self.__parent__ = None
        self.uniqueId = self.url

    @zeit.web.reify
    def date_first_released(self):
        pub_date = self.xml.findtext('pubDate')
        if pub_date is not None:
            return email.utils.parsedate_tz(pub_date.strip())

    @zeit.web.reify
    def copyrights(self):
        if self.__parent__ is not None:
            return self.__parent__.xml.findtext('copyright')

    @zeit.web.reify
    def title(self):
        title = self.xml.findtext('title')
        if title is not None:
            return title.strip()

    @property
    def teaserTitle(self):  # NOQA
        return self.title

    @zeit.web.reify
    def supertitle(self):
        supertitle = self.xml.findtext('category')
        if supertitle is not None:
            return supertitle.strip()

    @property
    def teaserSupertitle(self):  # NOQA
        return self.supertitle

    @zeit.web.reify
    def text(self):
        return self.xml.findtext('description')

    @property
    def teaserText(self):  # NOQA
        return self.text

    @zeit.web.reify
    def url(self):
        return self.xml.findtext('link')

    @zeit.web.reify
    def image_url(self):
        enclosure = self.xml.find('enclosure')
        if enclosure is not None:
            return enclosure.get('url')

    @zeit.web.reify
    def is_ad(self):
        nsmap = dict(
            dc="http://purl.org/dc/elements/1.1/")
        dc_type = self.xml.find('dc:type', namespaces=nsmap)

        if dc_type is not None and getattr(dc_type, 'text') == 'native-ad':
            return True
        return False


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(IRSSLink)
def rsslink_to_imagegroup(context):
    imagegroup = zope.component.getAdapter(
        context,
        zeit.content.image.interfaces.IImageGroup,
        IRSSArea(context).kind)
    imagegroup.__parent__ = context
    return imagegroup


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(IRSSLink)
class RSSImages(zeit.web.core.image.RemoteImages):
    pass


@SHORT_TERM_CACHE.cache_on_arguments()
def _cache_feed(url, timeout):
    response = None
    try:
        with zeit.web.core.metrics.timer('feed.rss.reponse_time'):
            response = requests.get(url, timeout=timeout)
        return response.content
    finally:
        status = response.status_code if response else 599
        zeit.web.core.metrics.increment('feed.rss.status.%s' % status)


def parse_feed(url, kind, timeout=2):
    try:
        xml = lxml.etree.fromstring(_cache_feed(url, timeout))
    except (requests.exceptions.RequestException,
            lxml.etree.XMLSyntaxError), e:
        log.debug('Could not collect {}: {}'.format(url, e))
        return
    for item in xml.xpath('/rss/channel/item'):
        yield zope.component.getAdapter(item, IRSSLink, kind)


class IRSSArea(zeit.content.cp.interfaces.IArea):

    feed_key = zope.interface.Attribute('feed_key')


class RSSArea(zeit.content.cp.automatic.AutomaticArea):

    zope.interface.implements(IRSSArea)

    feed_key = NotImplemented

    def values(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get(self.feed_key)
        timeout = conf.get(self.feed_key + u'_timeout', 2)
        values = []

        for item in parse_feed(url, self.kind, timeout):
            module = zeit.web.core.centerpage.TeaserModule(
                [item], layout=self.module_layout)
            item.__parent__ = self
            module.type = 'teaser'
            values.append(module)

        return values

    @zeit.web.reify
    def module_layout(self):
        xpath = '//layout[contains(@default, "{}")]/@id'.format(self.kind)
        source = zeit.content.cp.layout.TEASERBLOCK_LAYOUTS
        layout = source.factory._get_tree().xpath(xpath)
        if len(layout) > 0:
            return layout[0]


@grokcore.component.implementer(IRSSArea)
@grokcore.component.adapter(IRSSLink)
def rsslink_to_rssarea(context):
    return context.__parent__
