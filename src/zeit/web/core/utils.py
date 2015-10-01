import collections
import logging
import re

import grokcore.component
import jinja2
import peak.util.proxies
import zope.component
import beaker.cache

import zeit.cms.interfaces
import zeit.content.image.interfaces


log = logging.getLogger(__name__)


@beaker.cache.cache_region('short_term', 'whitelist')
def _cached_whitelist():
    whitelist = zope.component.getUtility(
        zeit.cms.tagging.interfaces.IWhitelist)
    return whitelist


def _whitelist_by_url_value():
    whitelist = _cached_whitelist()
    return {tag.url_value: tag for tag in whitelist.values()}


def tag_by_url_value(tag_url_value):
    return _whitelist_by_url_value().get(tag_url_value, None)


def tag_by_uuid_value(tag_uuid_value):
    whitelist = _cached_whitelist()
    return whitelist[tag_uuid_value]


def fix_misrepresented_latin(val):
    """Fix misrepresentation of latin-1 chars in unicode strings."""

    if isinstance(val, unicode):
        try:
            val = val.encode('latin-1', 'backslashreplace').decode('utf-8')
        except UnicodeDecodeError:
            pass
    return val


def to_int(val, pattern=re.compile(r'[^\d.]+')):
    """Converts an arbitrary object with a unicode representation to an int
    by trashing all non-decimal chars from its unicode or str representation.

    :param val: Arbitrary input
    :rtype: int
    """

    if hasattr(val, '__unicode__') or isinstance(val, unicode):
        val = unicode(val).encode('ascii', 'ignore')
    return int(pattern.sub('', '0' + str(val)))


def get_named_adapter(obj, iface, attr, name=None):
    """Retrieve a named adapted for a given object and interface, with a name
    beeing extracted from a given attribute. If no adapter is found, fallback
    to the unnamed default or the initial object itself.

    :param obj: Object to be adapted
    :param iface: A zope interface class
    :param attr: Attribute of object to extract the name from
    :param name: Override argument for the name
    :rtype: Object that hopefully implements `iface`
    """

    try:
        return zope.component.getAdapter(
            obj, iface, getattr(obj, attr, u'') if name is None else name)
    except (zope.component.ComponentLookupError, TypeError):
        if name is None:
            return get_named_adapter(obj, iface, attr, u'')
    return obj


def find_block(context, attrib='cp:__name__', **specs):
    """Find a block (region/area/module/block/container/cluster, you name it)
    in the XML of a given context. You can pass in arbitrary keyword arguments
    that need to match the attributes of your desired block.
    You may also need to override the name of the uuid attribute using the
    attrib keyword.
    """
    # XXX Maybe this would also work with IXMLReference?
    # zope.component.queryAdapter(
    #     context, zeit.cms.content.interfaces.IXMLReference, name='related')

    tpl = jinja2.Template("""
        .//*[{% for k, v in specs %}@{{ k }}="{{ v }}"{% endfor %}]/@{{ attr }}
    """)
    unique_ids = context.xml.xpath(
        tpl.render(attr=attrib, specs=specs.items()).strip(),
        namespaces={'cp': 'http://namespaces.zeit.de/CMS/cp'})
    try:
        block = context.get_recursive(unique_ids[0])
        return zeit.cms.interfaces.ICMSContent(block.uniqueId)
    except (AttributeError, IndexError, TypeError):
        return


def first_child(iterable):
    """Safely returns the first child of an iterable or None, if the iterable
    is exhausted.

    :param iterable: Some kind of iterable
    :rtype: arbitrary object
    """

    try:
        return iter(iterable).next()
    except (AttributeError, TypeError, StopIteration):
        return


def neighborhood(iterable, default=None):
    """Sliding window generator function that yields a tuple in the form
    of (prev, item, next).
    :param iterable: Iterable to cycle through
    :param default: Default value to yield for undefined neighbors
    :rtype: types.GeneratorType
    """

    iterator = iter(iterable)
    prev, item = default, iterator.next()
    for next in iterator:
        yield prev, item, next
        prev, item = item, next
    yield prev, item, default


class nsmixin:
    """New style magic attribute methods as a mixin class."""

    __setattr__ = object.__setattr__
    __delattr__ = object.__delattr__


class nslist(list, nsmixin):
    """New style list class with attribute access and manipulation."""

    pass


class nstuple(tuple, nsmixin):
    """New style tuple class with attribute access and manipulation."""

    pass


class nsdict(dict, nsmixin):
    """New style dictionary class with attribute access and manipulation."""

    pass


class nsset(set, nsmixin):
    """New style set class with attribute access and manipulation."""

    pass


class nsstr(str, nsmixin):
    """New style string class with attribute access and manipulation."""

    pass


class nsunicode(unicode, nsmixin):
    """New style unicode class with attribute access and manipulation."""

    pass


class frozendict(dict):
    """Custom dictionary class that discourages item manipulation."""

    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = (
        NotImplemented)

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class attrdict(dict):
    """Custom dictionary class that allows item access via attribute names."""

    def __getattr__(self, key):
        return key in self and self[key] or self.__getattribute__(key)


class defaultdict(collections.defaultdict):
    """Extension of stdlib's defaultdict that overwrites its `get` method and
    behaviour of the `in` operator.
    """

    def get(self, key, *args):
        """If the key cannot be found, return the (optional) function scope
        default or the defaultdict instances default.

        :param key: Key of the dictionary item to be retrieved.
        :param default: Opional function scope default value.
        """
        length = len(args)
        if length > 1:
            raise TypeError(
                'get() expected at most 2 arguments, got {}'.format(length))
        elif length == 1:
            return super(defaultdict, self).get(key) or args[0]
        return self.__getitem__(key)

    def __contains__(self, name):
        """Instances of defaultdict will pretend to contain any key."""
        return True


class defaultattrdict(attrdict, defaultdict):
    """Combines the best of both the default- and the attrdict."""

    def __getattr__(self, key):
        return self[key]


@grokcore.component.adapter(dict)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
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

    def __init__(self, context, istack=[zeit.cms.interfaces.ICMSContent]):
        def callback():
            factory = context.get('uniqueId', None)
            istack = iter(self.__istack__)
            while True:
                try:
                    iface = next(istack)
                    factory = iface(factory)
                except (StopIteration, TypeError,
                        zope.component.ComponentLookupError):
                    object.__setattr__(self, '__exposed__', True)
                    return factory

        origin = peak.util.proxies.LazyProxy(callback)
        object.__setattr__(self, '__exposed__', False)
        object.__setattr__(self, '__istack__', istack)
        object.__setattr__(self, '__origin__', origin)
        object.__setattr__(self, '__proxy__', context)

    def __getattr__(self, key):
        if not self.__exposed__ or not hasattr(self.__origin__, key):
            try:
                return self.__proxy__[key]
            except KeyError:
                log.debug(u"ProxyExposed: '{}' has no attribute '{}'".format(
                    self, key))
        return getattr(self.__origin__, key)

    def __setattr__(self, key, value):
        if self.__exposed__:
            setattr(self.__origin__, key, value)
        else:
            # TODO: Properly defer attribute setter until origin is exposed.
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

    # Proxy zeit.content.image.interfaces.IImages. Since we bypass ZCA
    # in __conform__ above, we cannot use an adapter to do this. ;-)
    @property
    def image(self):
        context = self.__proxy__
        image_ids = context.get('image-base-id', [])
        if not image_ids:
            raise AttributeError('image')
        return zeit.cms.interfaces.ICMSContent(image_ids[0])

    # Proxy zeit.content.link.interfaces.ILink.blog.
    # (Note: templates try to access this directly without adapting first.)
    @property
    def blog(self):
        context = self.__proxy__
        if context.get('type') != 'link':
            return False
        raise AttributeError('blog')
