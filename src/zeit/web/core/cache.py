# -*- coding: utf-8 -*-
import zope.interface
import zope.component
import grokcore.component

import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces


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
