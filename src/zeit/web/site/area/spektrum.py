import logging
import urllib2

import grokcore.component
import lxml.etree
import lxml.objectify
import requests
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.image

import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.core.metrics


log = logging.getLogger(__name__)


FIELD_MAP = {
    'title': 'teaserTitle',
    'description': 'teaserText',
    'link': 'url',
    'guid': 'guid'
}


class Teaser(object):

    def __init__(self, item):
        for value in FIELD_MAP.values():
            setattr(self, value, '')

        self.feed_image = None
        self.teaserSupertitle = ''
        self.uniqueId = None

        for value in item:
            if value.tag in FIELD_MAP.keys() and value.text:
                setattr(self, FIELD_MAP[value.tag], value.text.strip())
            elif value.tag == 'enclosure' and 'url' in value.keys():
                self.feed_image = value.get('url')

        self.teaserSupertitle, self.teaserTitle = self._split(self.teaserTitle)

    def _split(self, title):
        if ':' in title:
            return (title[:title.find(':')].strip(),
                    title[title.find(':') + 1:].strip())
        return ('', title)

    @property
    def image(self):
        try:
            return zeit.web.core.interfaces.ITeaserImage(self)
        except TypeError:
            return


@zeit.web.register_area('spektrum')
class HPFeed(object):

    def __new__(cls, *args):
        """Generate a list of teasers from an RSS feed."""
        import zeit.web.site.view_centerpage  # Circularity prevention
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = conf.get('spektrum_hp_feed')
        area = zeit.web.site.view_centerpage.LegacyArea(
            [], kind='spektrum')
        try:
            with zeit.web.core.metrics.timer('feed.spektrum.reponse_time'):
                resp = requests.get(feed_url, timeout=2.0)
            xml = lxml.etree.fromstring(resp.content)
            for i in xml.xpath('/rss/channel/item'):
                module = zeit.web.site.view_centerpage.LegacyModule(
                    [Teaser(i)], layout='parquet-spektrum')
                module.type = 'teaser'
                area.append(module)
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError), e:
            log.warn('Could not collect spektrum feed: %s' % e)
        return area


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(Teaser)
class SpektrumImage(zeit.web.core.block.BaseImage):

    def __init__(self, context):
        super(SpektrumImage, self).__init__()

        if context.feed_image is None:
            raise TypeError('Could not adpat', context,
                            zeit.web.core.interfaces.ITeaserImage)

        self.image = zeit.content.image.image.LocalImage()

        try:
            with self.image.open('w') as fh:
                fileobj = urllib2.urlopen(context.feed_image, timeout=4)
                fh.write(fileobj.read())
        except IOError:
            raise TypeError('Image was not found on spektrum server.')

        self.mimeType = fileobj.headers.get('Content-Type')
        self.image_pattern = 'spektrum'
        self.caption = context.teaserText
        self.title = context.teaserTitle
        self.alt = context.teaserTitle
        self.uniqueId = 'http://xml.zeit.de/spektrum-image{}'.format(
            context.feed_image.replace('http://www.spektrum.de', ''))
