# -*- coding: utf-8 -*-
import colander
import datetime
import urllib2
import urllib
import json
import zeit.cms.interfaces
from babel.dates import get_timezone
from comments import comments_per_unique_id


class UnavailableSectionException(Exception):
    pass


class UnavailableServiceException(Exception):
    pass


class LimitOutOfBoundsException(Exception):
    pass


class LinkReach(object):

    services = ['twitter', 'facebook', 'googleplus']
    sections = ['zeit-magazin']

    def __init__(self, stats_path, linkreach):
        self.stats_path = stats_path
        self.linkreach = linkreach

    def fetch_service(self, service, limit, section='zeit-magazin'):
        if section not in self.sections:
            raise UnavailableSectionException('No section named: ' + section)

        if service not in self.services:
            raise UnavailableServiceException('No service named: ' + service)

        if not 0 < limit < 10:
            raise LimitOutOfBoundsException('Limit must be between 0 and 10.')

        params = urllib.urlencode({'limit': limit, 'section': section})
        url = '%s/zonrank/%s?%s' % (self.linkreach, service, params)

        response = urllib2.urlopen(url, timeout=4)

        return DataSequence().deserialize(json.load(response))

    def fetch_comments(self, limit, section='zeit-magazin'):
        if section not in self.sections:
            raise UnavailableSectionException('No section named: ' + section)

        if not 0 < limit < 10:
            raise LimitOutOfBoundsException('Limit must be between 0 and 10.')

        url = 'http://xml.zeit.de/cms/work/import/feeds/most_comments_%s.rss'
        feed = zeit.cms.interfaces.ICMSContent(url % section)

        item_list = []

        for rss_node in feed.xml.xpath('/rss/channel/item')[:limit]:
            web_path = rss_node.xpath('guid/text()')[0]
            rel_path = web_path[18:]
            xml_path = 'http://xml.zeit.de' + rel_path

            try:
                # Ignore item if CMS lookup fails.
                article = zeit.cms.interfaces.ICMSContent(xml_path)
            except RuntimeError:#TypeError:
                continue

            comment_stats = comments_per_unique_id(self.stats_path)

            item = dict(location=rel_path,
                        score=comment_stats.get(xml_path, 0),
                        supertitle=article.supertitle,
                        title=article.title,
                        subtitle=article.subtitle,
                        section=article.ressort
                        )
            item_list.append(item)

        return DataSequence().deserialize(item_list)


def _prepare_date(value):
    if not isinstance(value, int):
        return None
    tz = get_timezone('Europe/Berlin')
    return datetime.datetime.fromtimestamp(value / 1000, tz)


class Entry(colander.MappingSchema):
    score = colander.SchemaNode(colander.Int())
    location = colander.SchemaNode(colander.String())
    supertitle = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date,
                                    missing=colander.drop
                                    )
    section = colander.SchemaNode(colander.String())
    fetchedAt = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date,
                                    missing=colander.drop
                                    )


class DataSequence(colander.SequenceSchema):
    entry = Entry()
