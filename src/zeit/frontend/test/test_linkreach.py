# -*- coding: utf-8 -*-
from zeit.frontend.reach import DataSequence
from zeit.frontend.reach import Entry
from zeit.frontend.reach import LinkReach
import datetime
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


def test_unavailable_service_should_throw_exception(app_settings):
    ch = app_settings['community_host']
    lh = app_settings['linkreach_host']
    with pytest.raises(zeit.frontend.reach.UnavailableServiceException):
        LinkReach(ch, lh).fetch_service('foo', 3)


def test_unavailable_section_should_throw_exceptions(app_settings):
    ch = app_settings['community_host']
    lh = app_settings['linkreach_host']
    with pytest.raises(zeit.frontend.reach.UnavailableSectionException):
        LinkReach(ch, lh).fetch_comments(3, section='foo')
    with pytest.raises(zeit.frontend.reach.UnavailableSectionException):
        LinkReach(ch, lh).fetch_service('twitter', 3, section='foo')


def test_out_of_bounds_limits_should_throw_exceptions(app_settings):
    ch = app_settings['community_host']
    lh = app_settings['linkreach_host']
    with pytest.raises(zeit.frontend.reach.LimitOutOfBoundsException):
        LinkReach(ch, lh).fetch_comments(0)
    with pytest.raises(zeit.frontend.reach.LimitOutOfBoundsException):
        LinkReach(ch, lh).fetch_comments(99)
    with pytest.raises(zeit.frontend.reach.LimitOutOfBoundsException):
        LinkReach(ch, lh).fetch_service('twitter', 0)
    with pytest.raises(zeit.frontend.reach.LimitOutOfBoundsException):
        LinkReach(ch, lh).fetch_service('twitter', 99)


def test_data_for_twitter_should_be_fetched(linkreach):
    data = linkreach.fetch_service('twitter', 3)
    assert len(data) == 3


def test_data_for_facebook_should_be_fetched(linkreach):
    data = linkreach.fetch_service('facebook', 3)
    assert len(data) == 3


def test_data_for_googleplus_should_be_fetched(linkreach):
    data = linkreach.fetch_service('googleplus', 3)
    assert len(data) == 3

def test_data_for_comments_should_be_fetched(application, linkreach):
    data = linkreach.fetch_comments(3)
    assert len(data) == 3
