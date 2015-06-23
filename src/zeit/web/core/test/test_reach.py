import zeit.content.article.interfaces

import zeit.web.core.reach


def test_reach_host_should_be_stored_in_instance(application):
    conn = zeit.web.core.reach.Reach()
    assert conn.host == 'http://reach.zeit.de:4044/api'


def test_reach_connection_should_be_stored_in_class(application):
    conn = zeit.web.core.reach.Reach()
    assert conn._session is zeit.web.core.reach.Reach._session


def test_data_for_twitter_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('twitter', 'zeit-magazin')
    assert len(data) == 3
    assert all(['teaserTitle' in a for a in data])


def test_data_for_facebook_should_be_fetched(application):
    data = zeit.web.core.reach.fetch('facebook', 'zeit-magazin')
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
