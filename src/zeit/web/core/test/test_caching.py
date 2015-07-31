# -*- coding: utf-8 -*-
import mock
import pyramid_beaker
import pytest
import zope.component

import zeit.cms.interfaces

import zeit.web.core.comments
import zeit.web.core.interfaces


@pytest.mark.parametrize(
    'content', [
        ('http://xml.zeit.de/artikel/01', 10),
        ('http://xml.zeit.de/autoren/anne_mustermann', 5),
        ('http://xml.zeit.de/centerpage/index', 20),
        ('http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer', 40),
    ])
def test_caching_time_should_be_set_per_content_object(application, content):
    obj = zeit.cms.interfaces.ICMSContent(content[0])
    assert zeit.web.core.cache.ICachingTime(obj) == content[1]


def test_response_should_have_intended_caching_time(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert browser.headers['cache-control'] == 'max-age=20'


def test_should_bypass_cache_on_memcache_server_error(application):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['cache.type'] = 'ext:memcached'
    settings['cache.url'] = 'localhost:99998'
    pyramid_beaker.set_cache_regions_from_settings(settings)
    with mock.patch('zeit.web.core.comments.request_thread') as request:
        request.return_value = ''
        zeit.web.core.comments.get_cacheable_thread(
            'http://xml.zeit.de/artikel/01')
        zeit.web.core.comments.get_cacheable_thread(
            'http://xml.zeit.de/artikel/01')
        assert request.call_count == 2
