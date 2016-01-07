# -*- coding: utf-8 -*-
import beaker.cache
import mock
import pytest

import zeit.web


try:
    import pylibmc
except:
    HAVE_PYLIBMC = False
else:
    HAVE_PYLIBMC = True


@pytest.mark.skipif(not HAVE_PYLIBMC, reason='pylibmc not installed')
def test_should_bypass_cache_on_memcache_server_error(application, request):
    with mock.patch.dict(
            beaker.cache.cache_regions['long_term'],
            {'type': 'ext:memcached', 'url': 'localhost:9998'}):

        @beaker.cache.cache_region('long_term', 'test_memcache')
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

    assert Foo.first.region is None
    assert Foo.second.region == 'default_term'


def test_reify_should_store_result_in_beaker_cache_region(application):
    class Context(object):
        uniqueId = u'http://xml.zeit.de/ünicöde'  # NOQA

    class Foo(object):
        context = Context

        @zeit.web.reify('long_term')
        def prop(self):
            return 71

    foo = Foo()
    cache = Foo.prop._get_cache(foo)
    assert cache.namespace_name == (
        'zeit.web.core.test.test_cache.Foo.prop')
    assert foo.prop == 71
    expected_hash = '85444f4b731a8cf8f8f05dcf7db95f19e1420542'
    assert Foo.prop._global_key(foo) == expected_hash
    assert cache.has_key(expected_hash)  # NOQA
    assert cache.get(expected_hash) == 71


@pytest.mark.skipif(not HAVE_PYLIBMC, reason='pylibmc not installed')
def test_reify_should_work_with_memcache(application, monkeypatch, request):
    # Don't suppress errors, detecting those is the whole point of this test.
    monkeypatch.setattr(
        beaker.ext.memcached.PyLibMCNamespaceManager, '__contains__',
        zeit.web.core.cache.original_contains)

    with mock.patch.dict(
            beaker.cache.cache_regions['long_term'],
            {'type': 'ext:memcached', 'url': 'localhost:9998'}):

        class Context(object):
            uniqueId = 'http://xml.zeit.de'  # NOQA

        class Foo(object):
            context = Context

            @zeit.web.reify('long_term')
            def prop(self):
                return 71

        foo = Foo()
        # We hope that we've hit any interesting integration issues if we make
        # it to the "actually connect to memcache" point.
        with pytest.raises(pylibmc.ConnectionError):
            assert foo.prop == 71


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
