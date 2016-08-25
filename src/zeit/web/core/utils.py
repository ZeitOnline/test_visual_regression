import collections
import datetime
import logging
import os
import os.path
import pkg_resources
import random
import re
import itertools
import urllib
import urlparse

import grokcore.component
import jinja2
import peak.util.proxies
import pysolr
import pytz
import zope.component

import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.solr.interfaces
import zeit.retresco.connection
import zeit.retresco.convert
import zeit.retresco.interfaces


log = logging.getLogger(__name__)
unset = object()


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


def update_get_params(url, **params):
    """Safely update a URL's query parameters, overwriting and sorting
    existing entries while preserving all other parts of the URL.

    :param url: Uniform resource locator
    :param params: New query parameters
    :rtype: unicode
    """

    parts = list(urlparse.urlparse(url))
    combined = dict(urlparse.parse_qs(parts[4]), **params)
    query = collections.OrderedDict(sorted(combined.items()))
    parts[4] = urllib.urlencode(query, doseq=True)
    return urlparse.urlunparse(parts)


def add_get_params(url, **kw):
    """Add parameters to a URL, while preserving all other parts of the URL.
    Main difference to update_get_params is, that existing parameters
    will _not_ be overwriteen.

    :param url: Uniform resource locator
    :param params: New query parameters
    :rtype: unicode
    """

    parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qs(parts[4]))
    params = [(k, v) for k, v in itertools.chain(
              (i for i in query.iteritems() if i[0] not in kw),
              (i for i in kw.iteritems() if i[1] is not None))]
    parts[4] = urllib.urlencode(params, doseq=True)
    return urlparse.urlunparse(parts)


def remove_get_params(url, *args):
    """Remove all URL's query parameters specified by args,
    while preserving all other parts of the URL.

    :param url: Uniform resource locator
    :param params: query parameter keys to be deleted
    :rtype: unicode
    """
    scheme, netloc, path, query, frag = urlparse.urlsplit(url)
    query_p = urlparse.parse_qs(query)
    for arg in args:
        query_p.pop(arg, None)
    if len(query_p) == 0:
        return u'{}://{}{}'.format(
            scheme, netloc, path)
    else:
        return u'{}://{}{}?{}'.format(
            scheme, netloc, path, urllib.urlencode(query_p, doseq=True))


def update_path(url, *segments):
    """Safely update a URL's path preserving all other parts of the URL.

    :param url: Uniform resource locator
    :param segments: New path segments
    :rtype: unicode
    """

    parts = list(urlparse.urlparse(url))
    parts[2] = u'/' + u'/'.join(s.strip('/') for s in segments if s.strip('/'))
    return urlparse.urlunparse(parts)


def get_named_adapter(obj, iface, attr=unset, name=unset):
    """Retrieve a named adapted for a given object and interface, with a name
    beeing extracted from a given attribute. If no adapter is found, fallback
    to the unnamed default or the initial object itself.

    :param obj: Object to be adapted
    :param iface: A zope interface class
    :param attr: Attribute of object to extract the name from
    :param name: Override argument for the name
    :rtype: Object that hopefully implements `iface`
    """

    if (attr is unset) == (name is unset):
        raise TypeError('Expected exactly one of attr or name.')
    elif name is unset:
        name = getattr(obj, attr, u'')
    try:
        return zope.component.getAdapter(obj, iface, name)
    except (zope.component.ComponentLookupError, TypeError):
        return zope.component.queryAdapter(obj, iface, u'')


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
        return context.get_recursive(unique_ids[0])
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


class nsmixin:  # NOQA
    """New style magic attribute methods as a mixin class."""

    __setattr__ = object.__setattr__
    __delattr__ = object.__delattr__


class nslist(list, nsmixin):  # NOQA
    """New style list class with attribute access and manipulation."""

    pass


class nstuple(tuple, nsmixin):  # NOQA
    """New style tuple class with attribute access and manipulation."""

    pass


class nsdict(dict, nsmixin):  # NOQA
    """New style dictionary class with attribute access and manipulation."""

    pass


class nsset(set, nsmixin):  # NOQA
    """New style set class with attribute access and manipulation."""

    pass


class nsstr(str, nsmixin):  # NOQA
    """New style string class with attribute access and manipulation."""

    pass


class nsunicode(unicode, nsmixin):  # NOQA
    """New style unicode class with attribute access and manipulation."""

    pass


class frozendict(dict):  # NOQA
    """Custom dictionary class that discourages item manipulation."""

    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = (
        NotImplemented)

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class attrdict(dict):  # NOQA
    """Custom dictionary class that allows item access via attribute names."""

    def __getattr__(self, key):
        return key in self and self[key] or self.__getattribute__(key)


class defaultdict(collections.defaultdict):  # NOQA
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


class defaultattrdict(attrdict, defaultdict):  # NOQA
    """Combines the best of both the default- and the attrdict."""

    def __getattr__(self, key):
        return self[key]


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
        # Silently swallow missing item for solr/tms, but expose for reach.
        if ('product' not in self.__proxy__ or
                self.__proxy__['product'] is NotImplemented):
            self.__proxy__.pop('product', None)
            raise AttributeError('product')
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'product'].source(self)
        for value in source:
            if value.id == self.__proxy__.get('product_id'):
                return value

    @property
    def serie(self):
        # Silently swallow missing item for solr/tms, but expose for reach.
        if ('serie' not in self.__proxy__ or
                self.__proxy__['serie'] is NotImplemented):
            self.__proxy__.pop('serie', None)
            raise AttributeError('serie')
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'serie'].source(self)
        return source.factory.values.get(self.__proxy__.get('serie'))

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


CONTENT_TYPE_SOURCE = zeit.cms.content.sources.CMSContentTypeSource()


def dump_request(response):
    """Debug helper. Pass a `requests` response and receive an executable curl
    command line.
    """
    request = response.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = ["'{0}: {1}'".format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(headers)
    return command.format(
        method=method, headers=headers, data=data, uri=uri)


class RandomContent(object):

    def _get_content(self):
        import zeit.web.core.view  # Prevent circular import
        parts = urlparse.urlparse('egg://zeit.web.core/data')
        repo = pkg_resources.resource_filename(parts.netloc, parts.path[1:])
        for root, subdirs, files in os.walk(repo):
            if not random.getrandbits(1):
                continue  # Skip some folders to speed things up.
            for filename in files:
                name = filename.replace('.meta', '')
                unique_id = os.path.join(
                    root.replace(repo, 'http://xml.zeit.de'), name)
                content = zeit.cms.interfaces.ICMSContent(unique_id, None)
                if zeit.web.core.view.known_content(content):
                    yield content


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
class DataSolr(RandomContent):
    """Fake Solr implementation that is used for local development."""

    def search(self, q, rows=10, **kw):
        log.debug('Mocking solr request ' + urllib.urlencode(
            kw.items() + [('q', q), ('rows', rows)], True))
        results = []
        for content in self._get_content():
            try:
                publish = zeit.cms.workflow.interfaces.IPublishInfo(
                    content)
                modified = zeit.cms.workflow.interfaces.IModified(
                    content)
                semantic = zeit.cms.content.interfaces.ISemanticChange(
                    content)
                results.append({
                    u'authors': content.authors,
                    u'date-last-modified': (
                        modified.date_last_modified.isoformat()),
                    u'date_first_released': (
                        publish.date_first_released.isoformat()),
                    u'date_last_published': (
                        publish.date_last_published.isoformat()),
                    u'last-semantic-change': (
                        semantic.last_semantic_change.isoformat()),
                    u'image-base-id': [
                        'http://xml.zeit.de/zeit-online/'
                        'image/filmstill-hobbit-schlacht-fuenf-hee/'],
                    u'lead_candidate': False,
                    u'product_id': content.product.id,
                    u'serie': None,
                    u'supertitle': content.supertitle,
                    u'teaser_text': content.teaserText,
                    u'title': content.title,
                    u'type': content.__class__.__name__.lower(),
                    u'uniqueId': content.uniqueId})
            except (AttributeError, TypeError):
                continue
        return pysolr.Results(
            random.sample(results, min(rows, len(results))), len(results))

    def update_raw(self, xml, **kw):
        pass


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
class DataTMS(zeit.retresco.connection.TMS, RandomContent):
    """Fake TMS implementation that is used for local development."""

    def __init__(self):
        self._response = {}

    def _request(self, request, **kw):
        return self._response

    def get_topicpage_documents(self, id, start=0, rows=25):
        log.debug(
            'Mocking TMS request id=%s, start=%s, rows=%s', id, start, rows)
        result = []
        for content in self._get_content():
            data = zeit.retresco.interfaces.ITMSRepresentation(content)()
            if data is not None:
                # Ensure we always have an image
                data['payload'].setdefault(
                    'teaser_image',
                    'http://xml.zeit.de/zeit-online/'
                    'image/filmstill-hobbit-schlacht-fuenf-hee/')
                result.append(data)
        self._response = {
            'num_found': len(result),
            'docs': random.sample(
                result, min(rows, len(result))),
        }
        result = super(DataTMS, self).get_topicpage_documents(id, start, rows)
        self._response = {}
        return result


class CMSSearch(zeit.retresco.convert.Converter):

    interface = zeit.cms.interfaces.ICMSContent
    grokcore.component.name('zeit.find')

    def __call__(self):
        # Disable vivi-specific Converter, as it does not work without Zope.
        return {}
