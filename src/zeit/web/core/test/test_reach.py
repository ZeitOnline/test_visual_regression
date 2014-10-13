# -*- coding: utf-8 -*-
import pytest

import zeit.content.article.interfaces


is_article = zeit.content.article.interfaces.IArticle.providedBy


def test_unavailable_service_should_throw_exception(linkreach):
    with pytest.raises(ValueError):
        linkreach.fetch('N/A', 'zeit-magazin', 3)


def test_unavailable_section_should_not_throw_exceptions(linkreach):
    assert linkreach.fetch('comments', 'N/A', 3) == []
    assert linkreach.fetch('mostread', 'N/A', 3) == []
    assert linkreach.fetch('twitter', 'N/A', 3) == []


def test_out_of_bounds_limits_should_throw_exceptions(linkreach):
    with pytest.raises(ValueError):
        linkreach.fetch('comments', 'zeit-magazin', 0)
    with pytest.raises(ValueError):
        linkreach.fetch('comments', 'zeit-magazin', 99)
    with pytest.raises(ValueError):
        linkreach.fetch('mostread', 'zeit-magazin', 0)
    with pytest.raises(ValueError):
        linkreach.fetch('mostread', 'zeit-magazin', 99)
    with pytest.raises(ValueError):
        linkreach.fetch('twitter', 'zeit-magazin', 0)
    with pytest.raises(ValueError):
        linkreach.fetch('twitter', 'zeit-magazin', 99)


def test_data_for_twitter_should_be_fetched(application, linkreach):
    data = linkreach.fetch('twitter', 'zeit-magazin', 3)
    assert len(data) == 3
    assert all([is_article(a) for a in data])


def test_data_for_facebook_should_be_fetched(application, linkreach):
    data = linkreach.fetch('facebook', 'zeit-magazin', 3)
    assert len(data) == 3
    assert all([is_article(a) for a in data])


def test_data_for_googleplus_should_be_fetched(application, linkreach):
    data = linkreach.fetch('googleplus', 'zeit-magazin', 3)
    assert len(data) == 3
    assert all([is_article(a) for a in data])


def test_data_for_comments_should_be_fetched(application, linkreach):
    data = linkreach.fetch('comments', 'zeit-magazin', 3)
    assert len(data) == 3
    assert all([is_article(a) for a in data])


def test_data_for_mostread_should_be_fetched(application, linkreach):
    data = linkreach.fetch('mostread', 'zeit-magazin', 3)
    assert len(data) == 3
    assert all([is_article(a) for a in data])


def test_counts_per_url_are_fetchable(application, linkreach):
    data = linkreach.get_counts_by_url('index')
    assert {'googleplus', 'twitter', 'facebook'}.issubset(data)


def test_unreachable_url_fails_gracefully(application, linkreach):
    data = linkreach.get_counts_by_url('N/A')
    assert data == {}
