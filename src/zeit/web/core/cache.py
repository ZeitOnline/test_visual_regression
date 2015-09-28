# -*- coding: utf-8 -*-
import logging

import beaker.ext.memcached
import grokcore.component
import zope.interface
import zope.component

import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces

import zeit.web.core.image


log = logging.getLogger(__name__)


class ICachingTime(zope.interface.Interface):

    """Provide a caching time in seconds for a content object such as
    ICMSContent.
    """


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
def caching_time_content(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_content', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
def caching_time_article(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_article', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
def caching_time_cp(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_centerpage', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
def caching_time_gallery(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_gallery', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
def caching_time_image(context):
    expires = zeit.web.core.image.image_expires(context)
    if expires is not None:
        return max(expires, 0)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_image', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def caching_time_videostill(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_videostill', '0'))


@grokcore.component.implementer(ICachingTime)
@grokcore.component.adapter(basestring)
def caching_time_external(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_external', '0'))


def contains_ignore_server_error(self, *args, **kw):
    try:
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
        return original_setvalue(self, *args, **kw)
    except:
        log.warning(
            'Error connecting to memcache at %s', self.mc.addresses)
        return False
original_setvalue = beaker.ext.memcached.PyLibMCNamespaceManager.set_value
beaker.ext.memcached.PyLibMCNamespaceManager.set_value = (
    setvalue_ignore_server_error)
