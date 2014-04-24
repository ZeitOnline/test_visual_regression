# -*- coding: utf-8 -*-
import colander
import datetime
import urllib2
import json
import comments
import zeit.cms.interfaces
from lxml import etree
from babel.dates import get_timezone



class UnavailablSectiontException(Exception):
    pass


class UnavailableServiceException(Exception):
    pass


class LimitOutOfBoundsException(Exception):
    pass


class LinkReach(object):

    services = ['twitter', 'facebook', 'googleplus']
    sections = ['zeit-magazin']

    def __init__(self, community_host, linkreach_host):
        self.community_host = community_host
        self.linkreach_host = linkreach_host

    def fetch_service(self, service, limit):
        # TODO: Does the linkreach API allow for section filters?
        if service not in self.services:
            raise UnavailableServiceException('No service named: ' + service)
        if not 0 < limit < 10:
            raise LimitOutOfBoundsException('Limit must be greater than 0 '
                                            'and less than 10.')
        if not self.linkreach_host:
            return []

        url = '%s/zonrank/%s?limit=%s' % (self.linkreach_host, service, limit)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=4)
        return DataSequence().deserialize(json.load(response))

    def fetch_comments(self, section, limit):
        if section not in self.sections:
            raise UnavailableSectionException('Section not configured: '
                                                 + section)
        if not 0 < limit < 10:
            raise LimitOutOfBoundsException('Limit must be greater than 0 '
                                            'and less than 10.')

        url = '%s/agatho/commentsection/mostcommented/24/%s.xml' % \
              (self.community_host, section)

        try:
            tree = etree.parse(url)
        except IOError:
            return []

        item_list = []

        for rss_node in etree.parse(url).xpath('/rss/channel/item')[:limit]:
            web_path = rss_node.xpath('guid/text()')[0]
            rel_path = web_path[18:]
            xml_path = 'http://xml.zeit.de' + rel_path

            try:
                article = zeit.cms.interfaces.ICMSContent(xml_path)
            except TypeError:
                continue

            # TODO: Get real score, as soon as ZMO-538 is merged.
            item = dict(location=rel_path,
                        score=0, # comments.comments_per_unique_id(path),
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
