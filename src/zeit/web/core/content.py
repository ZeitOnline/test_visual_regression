import datetime
import logging
import sys

import bugsnag
import peak.util.proxies
import pytz
import zope.component
import zope.interface

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.video.video
import zeit.retresco.tag

from zeit.web.core.jinja import get_current_request_path


log = logging.getLogger(__name__)
CONTENT_TYPE_SOURCE = zeit.cms.content.sources.CMSContentTypeSource()


class ILazyProxy(zeit.cms.content.interfaces.ICommonMetadata):
    pass


@zope.component.adapter(dict)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent, ILazyProxy)
class LazyProxy(object):
    """Proxy class for ICMSContent implementations which expects a dict in its
    constructor containing a `uniqueId` key-value pair.
    The resulting adapter tries to obtain all accessed properties from keys
    in its underlying dictionary.
    The actual repository lookup and XML parsing is deferred until an
    unresolvable key is discovered or a magic method called.
    Proxies pretend to conform to any interface that is called upon them by
    spawning a sub-proxy with the new interface pushed to the resolution stack.

    >>> obj = LazyProxy({'uniqueId': 'xml://index', 'title': 'Lorem ipsum'})
    >>> obj.title
    'Lorem ipsum'
    >>> obj
    <zeit.cms.interfaces.ICMSContent proxy at 0x109bbe510>
    >>> obj.author
    'Any one'
    >>> obj
    <zeit.content.cp.interfaces.ICenterPage proxy at 0x109bbe510>
    """

    def __new__(cls, context, istack=None):
        if not getattr(context, 'get', {}.get)('uniqueId', None):
            raise TypeError(
                'Could not adapt', context, zeit.cms.interfaces.ICMSContent)
        return object.__new__(cls)

    def __init__(self, context, istack=[zeit.cms.interfaces.ICMSContent]):
        import zeit.web.core.article  # Prevent circular imports

        def callback():
            object.__setattr__(self, '__exposed__', True)

            uniqueId = context.get('uniqueId', None)
            result = zeit.cms.interfaces.ICMSContent(uniqueId, None)
            if result is None:
                result = ExampleContentType()
                result.uniqueId = uniqueId

            for iface in self.__istack__[1:]:
                try:
                    result = iface(result)
                except (TypeError, zope.component.ComponentLookupError):
                    break
            return result

        origin = peak.util.proxies.LazyProxy(callback)
        object.__setattr__(self, '__exposed__', False)
        object.__setattr__(self, '__istack__', istack)
        object.__setattr__(self, '__origin__', origin)
        object.__setattr__(self, '__proxy__', context)

        # Let ourselves be treated like the actual content type we proxy for.
        if 'doc_type' in self.__proxy__:
            type_id = self.__proxy__['doc_type']
            # BBB for really old video objects that were indexed differently.
            if type_id == 'zeit.brightcove.interfaces.IVideo':
                type_id = 'video'
            # XXX Don't know who causes ext. solr to index this value
            elif type_id == 'centerpage':
                type_id = 'centerpage-2009'
            # XXX We should tweak the source_class so we don't have to talk to
            # `.factory`, but that's quite a bit of mechanical hassle.
            type_iface = CONTENT_TYPE_SOURCE.factory.find(type_id)
            if type_iface is not None:
                zope.interface.alsoProvides(self, type_iface)

        # XXX To be consistent with normal content, we should call
        # `zeit.web.core.repository.add_marker_interfaces(self)` here. However,
        # those adapters might access fields that are missing from solr/reach/
        # etc., because they are irrelevant for rendering teasers, thereby
        # unnecessarily exposing the proxy. (Also, reach currently does not
        # return the doc_type, so most adapters would not even apply.)
        # Thus, we hard-code yet another special case here, which normally is
        # handled by z.w.c.article.mark_according_to_series().
        if self.serie and self.serie.column:
            zope.interface.alsoProvides(
                self, zeit.web.core.article.IColumnArticle)

    def __getattr__(self, key):
        if not self.__exposed__ or not hasattr(self.__origin__, key):
            try:
                return self.__proxy__[key]
            except KeyError:
                exc_info = sys.exc_info()
                if key not in [
                        # Don't nag about fields definitely not indexed in solr
                        'autorships', 'image'
                        'blog', 'url',
                        'short_text', 'long_text'] + list(
                            zeit.push.interfaces.IAccountData):
                    bugsnag.notify(
                        exc_info[1],
                        traceback=exc_info[2],
                        context=get_current_request_path(),
                        grouping_hash=exc_info[1].args[0])
                log.debug(u"ProxyExposed: '{}' has no attribute '{}'".format(
                    self, key))
        return getattr(self.__origin__, key)

    def __setattr__(self, key, value):
        if self.__exposed__:
            setattr(self.__origin__, key, value)
        else:
            if key == '__provides__':  # XXX kludge to allow alsoProvides(type)
                object.__setattr__(self, key, value)
            else:
                # TODO Properly defer attribute setter until origin is exposed.
                self.__proxy__[key] = value

    def __delattr__(self, key):
        raise NotImplementedError()

    def __repr__(self):
        if self.__exposed__:
            cls = self.__origin__.__class__
        else:
            cls = self.__istack__[-1]
        if 'uniqueId' in self.__proxy__:
            location = u'for {}'.format(self.__proxy__['uniqueId'])
        else:
            location = u'at {}>'.format(hex(id(self)))
        return u'<{}.{} proxy {}>'.format(
            cls.__module__, cls.__name__, location)

    def __getitem__(self, key):
        if not self.__exposed__ or key not in self.__origin__:
            try:
                return self.__proxy__[key]
            except KeyError:
                log.debug(u"ProxyExposed: '{}' has no key '{}'".format(
                    self, key))
        return self.__origin__[key]

    def __setitem__(self, key, value):
        if self.__exposed__:
            self.__origin__[key] = value
        else:
            # TODO: Properly defer item setter until origin is exposed.
            self.__proxy__[key] = value

    def __delitem__(self, key):
        raise NotImplementedError()

    # XXX: Would have been a lot sleeker to generically produce the remaining
    #      magic methods. Not gonna happen though, see 3.4.12.
    #      https://docs.python.org/2/reference/datamodel.html

    def __hash__(self):
        return hash(self.__origin__)

    def __len__(self):
        return len(self.__origin__)

    def __bool__(self):
        return bool(self.__origin__)

    __nonzero__ = __bool__

    def __iter__(self):
        try:
            return iter(self.__origin__)
        except TypeError:
            return iter(())

    def __contains__(self, item):
        return item in self.__origin__

    def __dir__(self):
        return dir(self.__origin__)

    def __conform__(self, iface):
        return LazyProxy(self.__proxy__, self.__istack__ + [iface])

    # Proxy special ICommonMetadata attributes. (XXX copy&paste)
    @property
    def product(self):
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'product'].source(self)
        for value in source:
            if value.id == self.__proxy__.get('product_id'):
                return value

    @property
    def serie(self):
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'serie'].source(self)
        return source.find(self.__proxy__.get('serie'))

    @property
    def keywords(self):
        tags = []
        for label in self.__proxy__.get('keyword', ()):
            tags.append(zeit.retresco.tag.Tag(label, 'keyword'))
        return tags

    # Proxy zeit.content.image.interfaces.IImages. Since we bypass ZCA
    # in __conform__ above, we cannot use an adapter to do this. ;-)
    @property
    def image(self):
        image_id = self.__proxy__.get('teaser_image')
        if not image_id:
            raise AttributeError('image')
        return zeit.cms.interfaces.ICMSContent(image_id, None)

    # Proxy zeit.content.image.interfaces.IImages
    @property
    def fill_color(self):
        fill_color = self.__proxy__.get('teaser_image_fill_color')
        if fill_color:
            return fill_color
        # Since most images don't have a fill color, it's not worth exposing
        # the proxy just for this. But in some cases, we'll be exposed anyway,
        # e.g. for ISeriesArticleWithFallbackImage, and then we make use of it.
        elif self.__exposed__:
            return self.__origin__.fill_color

    # Proxy zeit.web.core.interfaces.IExpiration
    @property
    def is_expired(self):
        import zeit.web.core.date  # Prevent circular imports
        date = zeit.web.core.date.parse_date(
            self.__proxy__.get('image-expires', None))
        if date is None:
            return False
        now = datetime.datetime.now(pytz.UTC)
        return int((now - date).total_seconds()) > 0

    # Proxy zeit.content.link.interfaces.ILink.blog.
    # (Note: templates try to access this directly without adapting first.)
    @property
    def blog(self):
        if self.__proxy__.get('type') != 'link':
            return False
        raise AttributeError('blog')

    # Proxy zeit.content.video.interfaces.IVideo.seo_slug
    @property
    def seo_slug(self):
        return zeit.content.video.video.Video.seo_slug.__get__(self)

    # Proxy zeit.content.volume.interfaces.IVolume.get_cover
    # Returns main product_id by default as a fallback
    def get_cover(self, cover_id, product_id=None):
        # We ignore product_id, since it's only relevant for content talking
        # about its volume, not for a teaser of the volume itself (which is all
        # LazyProxy is concerned with).
        for key, value in self.__proxy__.items():
            if key.startswith('cover_'):
                name = key.replace('cover_', '', 1)
                if cover_id == name:
                    return zeit.cms.interfaces.ICMSContent(value, None)
        log.debug(
            u"ProxyExposed: '{}' could not emulate 'get_cover'".format(self))
        return self.__origin__.get_cover(cover_id)
