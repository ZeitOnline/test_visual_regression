# -*- coding: utf-8 -*-
import colander
import datetime
import urllib2
import json
from babel.dates import get_timezone


class UnprovidedService(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class LinkReach(object):

    services = ['twitter', 'facebook', 'googleplus']

    def __init__(self, linkreach_host):
        self.entry_point = linkreach_host

    def fetch_data(self, service, limit):
        if service not in self.services:
            raise UnprovidedService('No service named: ' + service)
        url = '%s/zonrank/%s?limit=%s' % (
            self.entry_point,
            service,
            limit,
        )

        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=4)
        return DataSequence().deserialize(json.load(response))


def _prepare_date(value):
    tz = get_timezone('Europe/Berlin')
    return datetime.datetime.fromtimestamp(value / 1000, tz)


class Entry(colander.MappingSchema):

    score = colander.SchemaNode(colander.Int())
    location = colander.SchemaNode(colander.String())
    supertitle = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date)
    section = colander.SchemaNode(colander.String())
    fetchedAt = colander.SchemaNode(colander.Int(),
                                     preparer=_prepare_date)


class DataSequence(colander.SequenceSchema):
    entry = Entry()
