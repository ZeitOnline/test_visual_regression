# -*- coding: utf-8 -*-
import colander
import datetime
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


def _prepare_date(value):
    tz = get_timezone('Europe/Berlin')
    return datetime.datetime.fromtimestamp(value/1000, tz)


class _Entry(colander.MappingSchema):

    score = colander.SchemaNode(colander.Int(),
                                validator=colander.Range(0, 9999))
    location = colander.SchemaNode(colander.String())
    supertitle = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.Int(),
                                    preparer=_prepare_date)
    section = colander.SchemaNode(colander.String())
    fetched_at = colander.SchemaNode(colander.Int(),
                                     preparer=_prepare_date)


class Entry(object):

    def __init__(self, entries):
        self.__dict__.update(entries)
