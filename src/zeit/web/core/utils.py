import collections
import re
import itertools
import urllib
import urlparse

import jinja2
import zope.component

import zeit.web.core.interfaces


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

    if isinstance(url, unicode):
        url = url.encode('utf-8')

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


def maybe_convert_http_to_https(url):
    if not url:
        return
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    rewrite_https_links = conf.get('transform_to_secure_links_for',
                                   '').split(',')
    scheme, netloc, path, params, query, fragments = urlparse.urlparse(url)
    if scheme != 'http':
        return url
    if netloc not in rewrite_https_links:
        return url
    metrics = zope.component.getUtility(zeit.web.core.interfaces.IMetrics)
    metrics.increment('protocol_converted')
    return urlparse.urlunparse(('https', netloc, path, params, query,
                               fragments))
