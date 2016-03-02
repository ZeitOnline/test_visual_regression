import datetime
import pytest
import pytz

import zeit.cms.interfaces

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
    assert zeit.web.core.interfaces.ICachingTime(obj) == content[1]


def test_response_should_have_intended_caching_time(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    assert browser.headers['cache-control'] == 'max-age=20'


def test_caching_time_for_image_should_respect_group_expires(
        application, clock):
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube')
    now = datetime.datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
    clock.freeze(now)
    expires = now + datetime.timedelta(seconds=5)
    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    workflow.released_to = expires
    assert zeit.web.core.interfaces.ICachingTime(group['wide']) == 5


def test_already_expired_image_should_have_caching_time_zero(
        application, clock):
    # Actually we probably never want to _serve_ such images in the first
    # place, so the caching time is more for completeness' sake.
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube')
    now = datetime.datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
    clock.freeze(now)
    expires = now - datetime.timedelta(seconds=5)
    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    workflow.released_to = expires
    assert zeit.web.core.interfaces.ICachingTime(group['wide']) == 0
