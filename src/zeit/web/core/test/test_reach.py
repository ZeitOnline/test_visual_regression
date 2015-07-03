# -*- coding: utf-8 -*-
import requests
import requests_file
import zope.component

import zeit.content.article.interfaces

import zeit.web.core.interfaces
import zeit.web.core.reach


def test_reach_host_should_be_configured_in_instance(application):
    conn = zeit.web.core.reach.Reach()
    assert conn.host.endswith('zeit.web/src/zeit/web/core/data/linkreach/api/')


def test_reach_connection_should_be_stored_in_class(application):
    conn = zeit.web.core.reach.Reach()
    assert conn.session is zeit.web.core.reach.Reach.session
    assert isinstance(conn.session, requests.Session)


def test_mock_reach_connection_should_handle_file_scheme(application):
    conn = zeit.web.core.reach.MockReach()
    adapter = conn.session.get_adapter('file://')
    assert isinstance(adapter, requests_file.FileAdapter)


def test_data_for_twitter_should_be_fetched(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_social(facet='twitter', section='zeit-magazin')
    assert len(data) == 3
    assert all(['uniqueId' in a for a in data])


def test_data_for_facebook_should_be_fetched(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_social(facet='facebook', section='zeit-magazin')
    assert len(data) == 3
    assert all(['uniqueId' in a for a in data])


def test_data_for_comments_should_be_fetched(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_comments(section='zeit-magazin')
    assert len(data) == 3
    assert all(['uniqueId' in a for a in data])


def test_data_for_mostread_should_be_fetched(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_views(section='zeit-magazin')
    assert len(data) == 3
    assert all(['uniqueId' in a for a in data])


def test_counts_per_url_are_fetchable(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_buzz('http://xml.zeit.de/index')
    assert {'social', 'comments', 'views', 'score'}.issubset(data.keys())


def test_non_ascii_url_fails_gracefully(application):
    reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
    data = reach.get_buzz(u'http://xml.zeit.de/ümläut')
    assert data == {}
