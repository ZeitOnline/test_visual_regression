import logging

import zope.component
import requests
import lxml.etree
import lxml.objectify

import zeit.content.cp.interfaces
import zeit.cms.interfaces

from zeit.web.site.view_centerpage import LegacyArea
from zeit.web.site.view_centerpage import LegacyModule
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view_centerpage
import zeit.web.site.view


log = logging.getLogger(__name__)


class Teaser(object):

    _map = {'title': 'teaserTitle',
            'description': 'teaserText',
            'link': 'url',
            'guid': 'guid'}

    uniqueId = None

    def __init__(self, item):
        for value in self._map.values():
            setattr(self, value, '')

        self.feed_image = None
        self.teaserSupertitle = ''

        for value in item:
            if value.tag in self._map.keys() and value.text:
                setattr(self, self._map[value.tag], value.text.strip())
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
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = conf.get('spektrum_hp_feed')
        area = LegacyArea([], kind='spektrum')
        try:
            resp = requests.get(feed_url, timeout=2.0)
            xml = lxml.etree.fromstring(resp.content)
            for i in xml.xpath('/rss/channel/item'):
                module = LegacyModule([Teaser(i)], layout='parquet-spektrum')
                module.type = 'teaser'
                area.append(module)
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError), e:
            log.warn('Could not collect spektrum feed: %s' % e)
        return area
