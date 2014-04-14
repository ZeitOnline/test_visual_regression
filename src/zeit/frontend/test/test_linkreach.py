# -*- coding: utf-8 -*-
from zeit.frontend.reach import DataSequence
from zeit.frontend.reach import Entry
from zeit.frontend.reach import LinkReach
import datetime
import pyramid.testing
import pytest
import zeit.frontend.reach


entry_data = {
    'score': 1235,
    'location': '/foo',
    'supertitle': 'my_supertitle',
    'title': 'my_title',
    'subtitle': 'my_subtitle',
    'timestamp': 1397127353368,
    'section': 'my_section',
    'fetchedAt': 1397127353368,
}


def test_entry_for_linkreach_should_deserialize():

    schema = Entry()
    entry = schema.deserialize(entry_data)

    assert entry['score'] == 1235
    assert entry['location'] == '/foo'
    assert entry['title'] == 'my_title'
    assert entry['subtitle'] == 'my_subtitle'
    assert entry['supertitle'] == 'my_supertitle'
    assert entry['section'] == 'my_section'

    my_date = datetime.datetime(2014, 4, 10, 12, 55, 53)
    assert entry['fetchedAt'].replace(tzinfo=None) == my_date
    assert entry['timestamp'].replace(tzinfo=None) == my_date


def test_data_sequence_for_linkreach_should_deserialize():
    data = [entry_data for x in range(1, 10)]
    schema = DataSequence()
    seq = schema.deserialize(data)
    assert len(seq) == 9


def test_not_provided_service_should_throw_exception():
    with pytest.raises(zeit.frontend.reach.UnprovidedService):
        LinkReach('file:///foo').fetch_data('foo', 20)

def test_data_for_twitter_should_be_fetched(linkreach):
    data = linkreach.fetch_data('twitter', 20)
    assert len(data) == 20

def test_data_for_facebook_should_be_fetched(linkreach):
    data = linkreach.fetch_data('facebook', 20)
    assert len(data) == 20

def test_data_for_googleplus_should_be_fetched(linkreach):
    data = linkreach.fetch_data('googleplus', 20)
    assert len(data) == 20
