# -*- coding: utf-8 -*-
import dogpile.cache
import dogpile.cache.backends.memcached
import mock
import pyramid_dogpile_cache2
import pytest

import zeit.web
import zeit.web.core.cache


try:
    import pylibmc
except:
    HAVE_PYLIBMC = False
else:
    HAVE_PYLIBMC = True


@pytest.mark.skipif(not HAVE_PYLIBMC, reason='pylibmc not installed')
def test_should_bypass_cache_on_memcache_server_error(application, request):
    region = dogpile.cache.make_region('test')
    region.configure(
        'dogpile.cache.pylibmc', arguments={'url': ['localhost:9998']})

    @region.cache_on_arguments()
    def use_cache(arg):
        calls.append(arg)
        return None

    calls = []

    use_cache(1)
    use_cache(1)
    assert len(calls) == 2


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

    assert Foo.first.cache_region is None
    assert Foo.second.cache_region.name == 'default_term'


def test_reify_should_store_result_in_cache_region(application):
    class Context(object):
        uniqueId = u'http://xml.zeit.de/ünicöde'  # NOQA

    class Foo(object):
        context = Context

        @zeit.web.reify('long_term')
        def prop(self):
            return 71

    foo = Foo()
    cache = Foo.prop.cache_region
    cache_key = Foo.prop._global_key(foo)
    assert cache_key == (
        u'zeit.web.core.test.test_cache.Foo.prop|http://xml.zeit.de/ünicöde')
    assert foo.prop == 71
    assert cache.get(cache_key) == 71


@pytest.mark.skipif(not HAVE_PYLIBMC, reason='pylibmc not installed')
def test_reify_should_work_with_memcache(application, monkeypatch, request):
    # Don't suppress errors, detecting those is the whole point of this test.
    monkeypatch.setattr(
        dogpile.cache.backends.memcached.GenericMemcachedBackend, 'get',
        zeit.web.core.cache.original_get)

    region = zeit.web.core.cache.get_region('test')
    region.configure(
        'dogpile.cache.pylibmc', arguments={'url': ['localhost:9998']})
    request.addfinalizer(
        lambda: pyramid_dogpile_cache2.CACHE_REGIONS.pop('test'))

    class Context(object):
        uniqueId = 'http://xml.zeit.de'  # NOQA

    class Foo(object):
        context = Context

        @zeit.web.reify('test')
        def prop(self):
            return 71

    foo = Foo()
    # We hope that we've hit any interesting integration issues if we make
    # it to the "actually connect to memcache" point.
    with pytest.raises(pylibmc.ConnectionError):
        assert foo.prop == 71


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
