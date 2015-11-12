# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import mock
import pyramid_beaker
import pytest
import pytz
import zope.component
import copy
import beaker.exceptions

import zeit.cms.interfaces

import zeit.web
import zeit.web.core.comments
import zeit.web.core.interfaces


try:
    import pylibmc
except:
    HAVE_PYLIBMC = False
else:
    HAVE_PYLIBMC = True


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


def test_caching_time_for_image_should_respect_group_expires(
        application, clock):
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube')
    now = datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
    clock.freeze(now)
    expires = now + timedelta(seconds=5)
    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    workflow.released_to = expires
    assert zeit.web.core.cache.ICachingTime(group['wide']) == 5


def test_already_expired_image_should_have_caching_time_zero(
        application, clock):
    # Actually we probably never want to _serve_ such images in the first
    # place, so the caching time is more for completeness' sake.
    group = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/exampleimages/artikel/01/schoppenstube')
    now = datetime(2015, 1, 1, 10, 0, tzinfo=pytz.UTC)
    clock.freeze(now)
    expires = now - timedelta(seconds=5)
    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    workflow.released_to = expires
    assert zeit.web.core.cache.ICachingTime(group['wide']) == 0


@pytest.mark.skipif(not HAVE_PYLIBMC, reason='pylibmc not installed')
def test_should_bypass_cache_on_memcache_server_error(application):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings_copy = copy.copy(settings)
    settings_copy['cache.type'] = 'ext:memcached'
    settings_copy['cache.url'] = 'localhost:99998'
    pyramid_beaker.set_cache_regions_from_settings(settings_copy)
    with mock.patch('zeit.web.core.comments.request_thread') as request:
        request.return_value = ''
        try:
            zeit.web.core.comments.get_cacheable_thread(
                'http://xml.zeit.de/artikel/01')
            zeit.web.core.comments.get_cacheable_thread(
                'http://xml.zeit.de/artikel/01')
        except beaker.exceptions.InvalidCacheBackendError:
            print "No valid beaker backend could be found."

        pyramid_beaker.set_cache_regions_from_settings(settings)
        assert request.call_count == 2


def test_reify_should_retain_basic_reify_functionality(application):
    function = mock.Mock(return_value=42)

    class Foo(object):
        @zeit.web.reify
        def prop(self):
            """Lorem ipsum aliqua laboris."""
            return function()

    foo = Foo()
    assert function.call_count == 0
    assert foo.prop == 42
    assert function.call_count == 1
    assert foo.prop == 42
    assert function.call_count == 1

    assert hasattr(foo, '__ff272e28369a8be16e74f5992b557564__')
    assert Foo.prop.func.__doc__ == 'Lorem ipsum aliqua laboris.'


def test_reify_should_set_region_parameter_accordingly(application):
    class Foo(object):
        @zeit.web.reify
        def first(self):
            pass

        @zeit.web.reify('default_term')
        def second(self):
            pass

    assert Foo.first.region is None
    assert Foo.second.region == 'default_term'


def test_reify_should_store_result_in_beaker_cache_region(application):
    class Context(object):
        uniqueId = 'http://xml.zeit.de'  # NOQA

    class Foo(object):
        context = Context

        @zeit.web.reify('long_term')
        def prop(self):
            return 71

    foo = Foo()
    cache = Foo.prop._get_cache(foo)
    assert cache.namespace_name == (
        u'<class \'zeit.web.core.test.test_caching.Foo\'>|prop')
    assert foo.prop == 71
    assert Foo.prop._global_key(foo).startswith('ee433f8b858201f4f5e3baf0c77')
    assert cache.has_key('ee433f8b858201f4f5e3baf0c7786237244b44ac')  # NOQA
    assert cache.get('ee433f8b858201f4f5e3baf0c7786237244b44ac') == 71


def test_reify_should_skip_second_layer_if_beaker_is_unavailable(application):
    function = mock.Mock(return_value=60)

    class Context(object):
        uniqueId = 'http://xml.zeit.de'  # NOQA

    class Hour(object):
        context = Context

        @zeit.web.reify('some_cache_region_that_aint_there')
        def seconds(self):
            return function()

    hour = Hour()
    assert hour.seconds == 60
    assert function.call_count == 1
    assert hour.seconds == 60
    assert function.call_count == 1
    hour = Hour()
    assert hour.seconds == 60
    assert function.call_count == 2


def test_reify_should_unpack_hitforpass_objects_and_skip_second_cache_layer(
        application):

    function = mock.Mock(return_value=zeit.web.dont_cache(60))

    class Context(object):
        uniqueId = 'http://xml.zeit.de'  # NOQA

    class Hour(object):
        context = Context

        @zeit.web.reify('short_term')
        def seconds(self):
            return function()

    hour = Hour()
    assert isinstance(hour.seconds, int)
    assert function.call_count == 1
    hour = Hour()
    assert hour.seconds == 60
    assert function.call_count == 2
