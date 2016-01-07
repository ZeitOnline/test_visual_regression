import logging

import beaker.ext.memcached

import zeit.web.core.metrics


log = logging.getLogger(__name__)


def contains_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('contains.memcache.response_time'):
            return original_contains(self, *args, **kw)
    except:
        log.warning(
            'Error connecting to memcache at %s', self.mc.addresses)
        return False
original_contains = beaker.ext.memcached.PyLibMCNamespaceManager.__contains__
beaker.ext.memcached.PyLibMCNamespaceManager.__contains__ = (
    contains_ignore_server_error)


def getitem_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('getitem.memcache.response_time'):
            return original_getitem(self, *args, **kw)
    except:
        log.warning(
            'Error connecting to memcache at %s', self.mc.addresses)
        return False
original_getitem = beaker.ext.memcached.PyLibMCNamespaceManager.__getitem__
beaker.ext.memcached.PyLibMCNamespaceManager.__getitem__ = (
    getitem_ignore_server_error)


def setvalue_ignore_server_error(self, *args, **kw):
    try:
        with zeit.web.core.metrics.timer('setvalue.memcache.response_time'):
            return original_setvalue(self, *args, **kw)
    except:
        log.warning(
            'Error connecting to memcache at %s', self.mc.addresses)
        return False
original_setvalue = beaker.ext.memcached.PyLibMCNamespaceManager.set_value
beaker.ext.memcached.PyLibMCNamespaceManager.set_value = (
    setvalue_ignore_server_error)
