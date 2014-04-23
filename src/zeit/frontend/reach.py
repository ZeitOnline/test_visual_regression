# -*- coding: utf-8 -*-
import colander
import datetime
import urllib2
import json
import comments
from babel.dates import get_timezone


class UnavailableDepartmentException(Exception):
    pass


class UnavailableServiceException(Exception):
    pass


class LimitOutOfBoundsException(Exception):
    pass


class LinkReach(object):

    services = ['twitter', 'facebook', 'googleplus']
    departments = ['zeit-magazin']

    def __init__(self, agatho_host, linkreach_host):
        self.agatho_host = agatho_host
        self.linkreach_host = linkreach_host

    def fetch_service(self, service, limit):
        if service not in self.services:
            raise UnavailableServiceException('No service named: ' + service)
        if not 0<limit<10:
            raise LimitOutOfBoundsException('Limit must be greater than 0 '
                                            'and less than 10.')
        if not self.linkreach_host:
            return []

        url = '%s/zonrank/%s?limit=%s' % (self.linkreach_host, service, limit)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=4)
        return DataSequence().deserialize(json.load(response))

    def fetch_comments(self, department, limit):
        if not department in self.departments:
            raise UnavailableDepartmentException('Departement not configured:'
                                                 ' ' + department)
        if not 0<limit<10:
            raise LimitOutOfBoundsException('Limit must be greater than 0 '
                                            'and less than 10.')
        if not self.agatho_host:
            return []

        url = '%s/%s' % (self.agatho_host, department)

        # TODO: Implement xml fetching and parsing.
        # req = urllib2.Request(url)
        # response = urllib2.urlopen(req, timeout=4)
        # comments.comments_per_unique_id('ID', 0)

        return DataSequence().deserialize([{'title': url}])


def _prepare_date(value):
    tz = get_timezone('Europe/Berlin')
    return datetime.datetime.fromtimestamp(value / 1000, tz)


class Entry(colander.MappingSchema):

    score = colander.SchemaNode(colander.Int())
    location = colander.SchemaNode(colander.String())
    supertitle = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.Int(), preparer=_prepare_date)
    section = colander.SchemaNode(colander.String())
    fetchedAt = colander.SchemaNode(colander.Int(), preparer=_prepare_date)


class DataSequence(colander.SequenceSchema):
    entry = Entry()
