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
        """Compile a list of popular articles for a specific service."""
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
        """Compile a list of most commented on articles."""
        if section not in self.sections:
            raise UnavailableSectionException('No section named: ' + section)

        if not 0 < limit < 10:
            raise LimitOutOfBoundsException('Limit must be between 0 and 10.')

        try:
            url = 'http://xml.zeit.de/import/feeds/most_comments_%s.rss'
            feed = zeit.cms.interfaces.ICMSContent(url % section)
        except TypeError:
            return []

        output = []

        iterator = iter(feed.xml.xpath('/rss/channel/item'))

        while len(output) < limit:
            # Compile list of most commented on articles.

            try:
                rss_node = iterator.next()
            except StopIteration:
                # Abort compiling comment list if feed is exhausted.
                break

            web_path = rss_node.xpath('guid/text()')[0]
            rel_path = web_path[18:]
            xml_path = 'http://xml.zeit.de' + rel_path

            try:
                article = zeit.cms.interfaces.ICMSContent(xml_path)
            except TypeError:
                # Ignore item if CMS lookup fails.
                continue

            try:
                score = comments_per_unique_id(self.stats_path)[rel_path]
            except KeyError:
                # Ignore item if comment count lookup fails.
                score = 0

            item = dict(location=rel_path,
                        score=score,
                        supertitle=article.supertitle,
                        title=article.title,
                        subtitle=article.subtitle,
                        section=article.ressort
                        )
            output.append(item)

        return DataSequence().deserialize(output)

    def get_counts_by_url(self, url):
        """Get share counts for all services for a specific URL."""
        params = urllib.urlencode({'url': url})
        url = '%s/reach?%s' % (self.linkreach, params)
        try:
            response = urllib2.urlopen(url, timeout=4).read()
            return json.loads(response)
        except (urllib2.HTTPError, urllib2.URLError, ValueError):
            return {}


def _prepare_date(value):
    if not isinstance(value, int):
        return None
    tz = get_timezone('Europe/Berlin')
    return datetime.datetime.fromtimestamp(value / 1000, tz)


class Entry(colander.MappingSchema):
    score = colander.SchemaNode(colander.Int(),
                                missing=colander.drop
                                )
    location = colander.SchemaNode(colander.String(),
                                   missing=colander.drop
                                   )
    supertitle = colander.SchemaNode(colander.String(),
                                     missing=colander.drop
                                     )
    title = colander.SchemaNode(colander.String(),
                                missing=colander.drop
                                )
    subtitle = colander.SchemaNode(colander.String(),
                                   missing=colander.drop
                                   )
    timestamp = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date,
                                    missing=colander.drop
                                    )
    section = colander.SchemaNode(colander.String(),
                                  missing=colander.drop
                                  )

    fetchedAt = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date,
                                    missing=colander.drop
                                    )


class DataSequence(colander.SequenceSchema):
    entry = Entry()
