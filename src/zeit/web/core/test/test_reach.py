# -*- coding: utf-8 -*-
import pytest

import zeit.content.article.interfaces

import zeit.web.core.reach


def test_unavailable_service_should_throw_exceptio():
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('N/A', 'zeit-magazin')


def test_unavailable_section_should_not_throw_exception():
    assert zeit.web.core.reach.fetch('comments', 'N/A') == []
    assert zeit.web.core.reach.fetch('mostread', 'N/A') == []
    assert zeit.web.core.reach.fetch('twitter', 'N/A') == []


def test_out_of_bounds_limits_should_throw_exception():
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('comments', 'zeit-magazin', limit=0)
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('comments', 'zeit-magazin', limit=99)
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('mostread', 'zeit-magazin', limit=0)
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('mostread', 'zeit-magazin', limit=99)
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('twitter', 'zeit-magazin', limit=0)
    with pytest.raises(ValueError):
        zeit.web.core.reach.fetch('twitter', 'zeit-magazin', limit=99)


def test_data_for_twitter_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('twitter', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_data_for_facebook_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('facebook', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_data_for_googleplus_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('googleplus', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_data_for_comments_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('comments', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_data_for_mostread_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('mostread', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_counts_per_url_are_fetchable(application):
    data = zeit.web.core.reach.fetch('path', 'index')
    assert {'googleplus', 'twitter', 'facebook'}.issubset(data)


def test_unreachable_url_fails_gracefully(application):
    data = zeit.web.core.reach.fetch('path', 'N/A')
    assert data == {}


def test_non_ascii_url_fails_gracefully(application):
    data = zeit.web.core.reach.fetch('path', u'ümläut')
    assert data == {}
