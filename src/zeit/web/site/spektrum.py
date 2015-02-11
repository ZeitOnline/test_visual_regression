# -*- coding: utf-8 -*-

import zope.component
import requests
import lxml.etree

import zeit.content.image.interfaces

import zeit.web.core.interfaces


class HPFeed(list):

    def __init__(self):
        """Generate a list of teasers from an RSS feed."""
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = conf.get('spektrum_hp_feed')

        try:
            resp = requests.get(feed_url, timeout=2.0)
            xml = lxml.etree.fromstring(resp.content)
            super(HPFeed, self).__init__(
                Teaser(i) for i in xml.xpath('/rss/channel/item'))
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError):
            super(HPFeed, self).__init__()


class Teaser(object):

    _map = {'title': 'teaserTitle',
            'description': 'teaserText',
            'link': 'url',
            'guid': 'guid'}

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
