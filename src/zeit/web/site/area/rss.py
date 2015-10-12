import email
import logging

import grokcore.component
import lxml.etree
import requests
import zope.component
import zope.interface

import zeit.content.cp.automatic
import zeit.content.image.interfaces
import zeit.content.link.interfaces

import zeit.web


log = logging.getLogger(__name__)


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

    @property
    def title(self):
        return self.teaserTitle

    @zeit.web.reify
    def teaserTitle(self):  # NOQA
        title = self.xml.findtext('title')
        if title and ': ' in title:
            return title.split(': ', 1)[1]
        return title

    @property
    def supertitle(self):
        return self.teaserSupertitle

    @zeit.web.reify
    def teaserSupertitle(self):  # NOQA
        title = self.xml.findtext('title')
        if title and ': ' in title:
            return title.split(': ', 1)[0]
        return ''

    @property
    def text(self):
        return self.teaserText

    @zeit.web.reify
    def teaserText(self):  # NOQA
        return self.xml.findtext('description')

    @zeit.web.reify
    def url(self):
        return self.xml.findtext('link')

    @zeit.web.reify
    def image_url(self):
        enclosure = self.xml.find('enclosure')
        if enclosure is not None:
            return enclosure.attrib.get('url')


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(IRSSLink)
class RSSImages(object):

    def __init__(self, context):
        self.context = context
        self.image = zeit.content.image.interfaces.IImageGroup(context)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(RSSLink)
def rsslink_to_imagegroup(context):
    # XXX: Okay this is still some nasty nasty no-no.
    return zope.component.getAdapter(
        context,
        zeit.content.image.interfaces.IImageGroup,
        context.__parent__.__class__.lower())


class RSSArea(zeit.content.cp.automatic.AutomaticArea):

    feed_key = NotImplemented
    module_layout = NotImplemented
    link_class = RSSLink

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        import zeit.web.core.interfaces
        import zeit.web.site.view_centerpage

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = conf.get(self.feed_key)
        values = []
        try:
            resp = requests.get(feed_url, timeout=2.0)
            xml = lxml.etree.fromstring(resp.content)
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError), e:
            log.debug('Could not collect {}: {}'.format(self.feed_key, e))
            return
        for i in xml.xpath('/rss/channel/item'):
            content = self.link_class(i)
            module = zeit.web.site.view_centerpage.LegacyModule(
                [content], layout=self.module_layout)
            content.__parent__ = self
            module.type = 'teaser'
            values.append(module)
        return values
