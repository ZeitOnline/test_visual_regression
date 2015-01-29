# -*- coding: utf-8 -*-
#import zope.component
#import zeit.web.core.interfaces
import requests
import lxml.etree

class HPFeed(object):

    def __init__(self, content):
        # zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        # feed_url = zwcs.get('spektrum_hp_feed')
        resp = requests.get('http://www.spektrum.de/alias/rss/zeit-kooperationsfeed/1329411')
        self.xml = lxml.etree.fromstring(resp.content)

    def __iter__(self):
        """Compile a list of teasers from an RSS feed.

        :param lxml.etree feed : RSS 2.0
        :rtype: dict
        """

        iterator = iter(self.xml.xpath('/rss/channel/item'))
        for item in iterator:
            yield Teaser(item)


class Teaser(object):

    _map = {'title': 'teaserTitle',
           'description': 'teaserText',
           'link': 'url',
           'enclosure': 'image'}

    def __init__(self, item):
        for value in item:
            if item.tag in self._map.keys:
                setattr(self, map[item.tag], item.text)
        if ':' in self.title:
            title = self.teaserTitle
            self.teaserSupertitle = title[:title.find(":")]
            self.teaserTitle = title[title.find(":")+1:]
