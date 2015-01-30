# -*- coding: utf-8 -*-

import zope.component
import requests
import lxml.etree

import zeit.web.core.interfaces


class HPFeed(object):

    def __init__(self):
        """Generate a list of teasers from an RSS feed.
        """

        self.xml = self._fetch_feed()

    def __iter__(self):
        iterator = iter(self.xml.xpath('/rss/channel/item'))
        for item in iterator:
            yield Teaser(item)

    def _fetch_feed(self):
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = zwcs.get('spektrum_hp_feed')
        resp = requests.get(feed_url)
        return lxml.etree.fromstring(resp.content)


class Teaser(object):

    _map = {'title': 'teaserTitle',
            'description': 'teaserText',
            'link': 'url'}

    def __init__(self, item):
        for value in self._map.values():
            setattr(self, value, '')
        self.teaserSupertitle = ''
        for value in item:
            if value.tag in self._map.keys() and value.text:
                setattr(self, self._map[value.tag], value.text.strip())
            elif value.tag == 'enclosure' and 'url' in value.keys():
                self._feed_image = value.get('url')
        self.teaserSupertitle, self.teaserTitle = self._split(self.teaserTitle)

    def _split(self, title):
        if ':' in title:
            return (title[:title.find(":")].strip(),
                    title[title.find(":") + 1:].strip())
        return ('', title)
