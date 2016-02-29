# -*- coding: utf-8 -*-
import logging
import random
import time

import dogpile.cache
import dogpile.cache.api
import dogpile.cache.backends.memcached
import pyramid_dogpile_cache2

import zeit.web.core.metrics


log = logging.getLogger(__name__)

# Convenience / encapsulation of caching infrastructure
get_region = pyramid_dogpile_cache2.get_region


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


def acquire_shorter_backoff(self, wait=True):
    try:
        with zeit.web.core.metrics.timer('acquire.memcache.response_time'):
            client = self.client_fn()
            for i in range(2):
                if client.add(self.key, 1, self.timeout):
                    return True
                elif not wait:
                    return False
                else:
                    sleep_time = 0.5 + (0.3 * random.random())
                    time.sleep(sleep_time)
    except:
        log.warning(
            'acquire: Error connecting to memcache at %s',
            self.client_fn().addresses)
        return False
dogpile.cache.backends.memcached.MemcachedLock.acquire = (
    acquire_shorter_backoff)


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
