import datetime

import pytest
import pytz
import zope.component

import zeit.cms.interfaces

import zeit.web.core.interfaces


@pytest.mark.parametrize(
    'content', [
        ('http://xml.zeit.de/zeit-magazin/article/01', 10),
        ('http://xml.zeit.de/autoren/anne_mustermann', 5),
        ('http://xml.zeit.de/zeit-magazin/centerpage/index', 20),
        ('http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer', 40),
    ])
def test_caching_time_should_be_set_per_content_object(application, content):
    obj = zeit.cms.interfaces.ICMSContent(content[0])
    assert zeit.web.core.interfaces.ICachingTime(obj) == content[1]


@pytest.fixture()
def video(application):
    return zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/1953013471001')


@pytest.fixture()
def article(application):
    return zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')


def test_brightcove_view_sets_marker(video, dummy_request):
    from zeit.web.core.view_image import Brightcove
    dummy_request.path_info = '/wide__280x157__desktop'
    brightcove_view = Brightcove(video, dummy_request)
    from zeit.web.core.interfaces import IExternalTemporaryImage
    assert IExternalTemporaryImage.providedBy(brightcove_view.context)


def test_regular_temporary_images_caching_time(application, article):
    temp_image = zeit.content.image.interfaces.IImageGroup(
        article.main_image.target)['wide__280x157__desktop']
    assert zeit.web.core.interfaces.ICachingTime(
        temp_image) == application.zeit_app.settings['caching_time_image']


def test_brightcove_temporary_images_have_external_caching(application, video):
    from zeit.content.image.interfaces import IImageGroup
    temp_image = IImageGroup(video)['wide__280x157__desktop']
    zope.interface.alsoProvides(
        temp_image,
        zeit.web.core.interfaces.IExternalTemporaryImage)
    assert (zeit.web.core.interfaces.ICachingTime(temp_image) ==
            application.zeit_app.settings['caching_time_external'])


def test_brightcove_temporary_images_have_external_varnish_caching(
        application, video):
    from zeit.content.image.interfaces import IImageGroup
    temp_image = IImageGroup(video)['wide__280x157__desktop']
    zope.interface.alsoProvides(
        temp_image,
        zeit.web.core.interfaces.IExternalTemporaryImage)
    assert zeit.web.core.interfaces.IVarnishCachingTime(temp_image) == 600


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


def test_longer_client_caching_time_overrides_varnish_time(testbrowser):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['caching_time_centerpage'] = 9999
    browser = testbrowser('/zeit-online/main-teaser-setup')
    assert browser.headers['cache-control'] == 'max-age=9999'


def test_sitemap_should_not_be_cached_in_varnish(application):
    sitemap = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/gsitemaps/index.xml')
    assert zeit.web.core.interfaces.IVarnishCachingTime(sitemap) == 0
