import grokcore.component
import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.content.video.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zope.interface.Interface)
def caching_time_default(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_default', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zope.interface.Interface)
def varnish_caching_time_default(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_default', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
def caching_time_content(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_content', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
def varnish_caching_time_content(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_content', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
def caching_time_article(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    # Toplevel content types should have 0, so that browsers re-request them
    # after login/logout, see BUG-343.
    return int(conf.get('caching_time_article', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
def varnish_caching_time_article(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_article', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
def caching_time_cp(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    # BUG-343
    return int(conf.get('caching_time_centerpage', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
def varnish_caching_time_cp(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_centerpage', '600'))


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
    # BUG-343
    return int(conf.get('caching_time_gallery', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
def varnish_caching_time_gallery(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_gallery', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def caching_time_video(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    # BUG-343
    return int(conf.get('caching_time_video', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def varnish_caching_time_video(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_video', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
def caching_time_image(context):
    expires = zeit.web.core.interfaces.IExpiration(context, None)
    expires = expires and expires.seconds
    if expires is not None:
        return max(expires, 0)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_image', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
def varnish_caching_time_image(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_image', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def caching_time_videostill(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_videostill', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
def varnish_caching_time_videostill(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_videostill', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.web.core.interfaces.INewsfeed)
def caching_time_feed(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_feed', '0'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.web.core.interfaces.INewsfeed)
def varnish_caching_time_feed(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_feed', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.image.image.TemporaryImage)
def caching_time_temporary_image(context):
    expires = zeit.web.core.interfaces.IExpiration(context, None)
    expires = expires and expires.seconds
    if expires is not None:
        return max(expires, 0)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_image', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.image.image.TemporaryImage)
def varnish_caching_time_temporary_image(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_image', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.web.core.interfaces.IExternalTemporaryImage)
def caching_time_external_image(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_external', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.web.core.interfaces.IExternalTemporaryImage)
def varnish_caching_time_external_image(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_external', '600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.text.interfaces.IText)
def caching_time_text(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_text', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.text.interfaces.IText)
def varnish_caching_time_text(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_text', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.content.rawxml.interfaces.IRawXML)
def caching_time_rawxml(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_rawxml', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.content.rawxml.interfaces.IRawXML)
def varnish_caching_time_rawxml(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_rawxml', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.cms.repository.interfaces.IFile)
def caching_time_unknown(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_file', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.cms.repository.interfaces.IFile)
def varnish_caching_time_unknown(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_file', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.ICachingTime)
@grokcore.component.adapter(zeit.cms.repository.interfaces.IUnknownResource)
def caching_time_unknown(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('caching_time_unknown', '3600'))


@grokcore.component.implementer(zeit.web.core.interfaces.IVarnishCachingTime)
@grokcore.component.adapter(zeit.cms.repository.interfaces.IUnknownResource)
def varnish_caching_time_unknown(context):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return int(conf.get('varnish_caching_time_unknown', '3600'))
