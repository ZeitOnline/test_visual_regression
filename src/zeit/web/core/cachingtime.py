import grokcore.component
import zope.component

import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
def caching_time_content(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_content', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
def varnish_caching_time_content(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_content', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
def caching_time_article(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_article', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
def caching_time_cp(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_centerpage', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.ISitemap)
def varnish_caching_time_sitemap(context):
    # Apparently, Google penalizes outdated sitemaps, so we're extra careful.
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_sitemap', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
def caching_time_gallery(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_gallery', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
def caching_time_image(context):
    expires = zeit.web.core.interfaces.IExpiration(context, None)
    expires = expires and expires.seconds
    if expires is not None:
        return max(expires, 0)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_image', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def caching_time_videostill(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_videostill', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.IFeed)
def caching_time_feed(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_feed', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.image.image.TemporaryImage)
def caching_time_external(context):
    expires = zeit.web.core.interfaces.IExpiration(context, None)
    expires = expires and expires.seconds
    if expires is not None:
        return max(expires, 0)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_external', '0'))
