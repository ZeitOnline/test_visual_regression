# -*- coding: utf-8 -*-
import pytest

import zeit.cms.interfaces

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
