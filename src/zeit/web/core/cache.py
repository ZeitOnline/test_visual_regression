# -*- coding: utf-8 -*-
import hashlib
import inspect
import logging

import dogpile.cache
import dogpile.cache.api
import dogpile.cache.backends.memcached

import zeit.web.core.metrics


log = logging.getLogger(__name__)


def get_region(name):
    """This is the main entry point to the caching system; it returns a
    CacheRegion that can be used to cache function results.

    Example usage::

        LONG_TERM_CACHE = zeit.web.core.cache.get_region('long_term')
        @LONG_TERM_CACHE.cache_on_arguments()
        def expensive_function(one, two, three):
            # compute stuff

    For properties of objects, you can also use @zeit.web.reify('long_term')
    instead of this. (XXX is having two ways for the same thing a good idea?)
    """
    if name not in CACHE_REGIONS:
        CACHE_REGIONS[name] = dogpile.cache.make_region(
            name,
            function_key_generator=key_generator,
            key_mangler=sha1_mangle_key)
    return CACHE_REGIONS[name]
CACHE_REGIONS = {}


def key_generator(ns, fn, to_str=unicode, cls=None):
    """Extension of dogpile.cache.util.function_key_generator that handles
    non-ascii function arguments, and supports not just plain functions, but
    methods, too (by passing `cls`).
    """
    if cls is not None:  # This is an extension, just for zeit.web.reify
        namespace = u'.'.join([cls.__module__, cls.__name__, fn.__name__])
    else:
        namespace = u'.'.join([fn.__module__, fn.__name__])

    if ns is not None:
        namespace = u'%s|%s' % (namespace, ns)

    args = inspect.getargspec(fn)
    has_self = args[0] and args[0][0] in ('self', 'cls')

    def generate_key(*args, **kw):
        if kw:
            raise ValueError(
                "dogpile.cache's default key creation "
                "function does not accept keyword arguments.")
        if has_self:
            args = args[1:]

        return namespace + u'|' + u' '.join(map(to_str, args))
    return generate_key


def sha1_mangle_key(key):
    """Extension of dogpile.cache.util.sha1_mangle_key that handles unicode."""
    return hashlib.sha1(key.encode('utf-8')).hexdigest()


# We treat caching as strictly optional, so we don't want to crash on memcache
# errors, but bypass caching instead. (We also collect timing metrics here.)

def get_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('get.memcache.response_time'):
            return original_get(self, *args, **kw)
    except:
        log.warning(
            'get: Error connecting to memcache at %s', self.client.addresses)
        return dogpile.cache.api.NO_VALUE
original_get = dogpile.cache.backends.memcached.GenericMemcachedBackend.get
dogpile.cache.backends.memcached.GenericMemcachedBackend.get = (
    get_ignore_server_error)


def set_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('set.memcache.response_time'):
            original_set(self, *args, **kw)
    except:
        log.warning(
            'set: Error connecting to memcache at %s', self.client.addresses)
original_set = dogpile.cache.backends.memcached.GenericMemcachedBackend.set
dogpile.cache.backends.memcached.GenericMemcachedBackend.set = (
    set_ignore_server_error)


def delete_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('delete.memcache.response_time'):
            original_delete(self, *args, **kw)
    except:
        log.warning(
            'delete: Error connecting to memcache at %s',
            self.client.addresses)
original_delete = (
    dogpile.cache.backends.memcached.GenericMemcachedBackend.delete)
dogpile.cache.backends.memcached.GenericMemcachedBackend.delete = (
    delete_ignore_server_error)


def acquire_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('acquire.memcache.response_time'):
            return original_acquire(self, *args, **kw)
    except:
        log.warning(
            'acquire: Error connecting to memcache at %s',
            self.client_fn().addresses)
        return False
original_acquire = (
    dogpile.cache.backends.memcached.MemcachedLock.acquire)
dogpile.cache.backends.memcached.MemcachedLock.acquire = (
    acquire_ignore_server_error)


def release_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('release.memcache.response_time'):
            original_release(self, *args, **kw)
    except:
        log.warning(
            'delete: Error connecting to memcache at %s',
            self.client_fn().addresses)
original_release = (
    dogpile.cache.backends.memcached.MemcachedLock.release)
dogpile.cache.backends.memcached.MemcachedLock.release = (
    release_ignore_server_error)
