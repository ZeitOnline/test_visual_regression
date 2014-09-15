from datetime import datetime, timedelta
import email.utils
import itertools
import logging
import mimetypes
import pkg_resources
import re
import time
import urllib2
import urlparse

from babel.dates import format_datetime
from lxml import objectify
from repoze.bitblt.transform import compute_signature
import jinja2
import jinja2.environment
import jinja2.runtime
import jinja2.utils
import jinja2.nodes
import pyramid.threadlocal
import pytz
import requests
import venusian
import zope.component

from zeit.frontend.utils import defaultdict
import zeit.cms.interfaces
import zeit.content.link.interfaces


log = logging.getLogger(__name__)

# Set during startup through application.py
default_teaser_images = None
image_scales = None


def JinjaEnvRegistrator(env_attr):
    """Factory function that returns a decorator configured to register a given
    environment attribute to the jinja context.

    :param str env_attr: Attribute name the returned decorator should register
    :returns: Decorator that registers functions to the jinja context
    :rtype: types.FunctionType
    """
    def registrator(func):
        """This decorator is non-destructive, meaning it does not replace the
        decorated function with a wrapped one. Instead, a callback is attached
        to the venusian scanner that is triggered at application startup.

        :internal:
        """
        def callback(scanner, name, obj):
            """Venusian callback that registers the decorated function under
            its `func_name` to the jinja `env_attr` passed to the registrator
            factory.

            :internal:
            """
            if hasattr(scanner, 'env') and env_attr in scanner.env.__dict__:
                scanner.env.__dict__[env_attr][name] = obj
        venusian.attach(func, callback, category='jinja')
        return func
    return registrator


register_filter = JinjaEnvRegistrator('filters')
register_global = JinjaEnvRegistrator('globals')
register_test = JinjaEnvRegistrator('tests')


class Undefined(jinja2.runtime.Undefined):
    """Custom jinja Undefined class that represents unresolvable template
    statements and expressions. It ignores undefined errors, ensures it is
    printable and returns further Undefined objects if indexed or called.
    """

    def __html__(self):
        return jinja2.utils.Markup()

    @jinja2.utils.internalcode
    def _fail_with_undefined_error(self, *args, **kw):
        pass

    __getattr__ = __getitem__ = __call__ = lambda self, *args: self.__class__()


class Environment(jinja2.environment.Environment):
    """Custom jinja Environment class that uses our custom Undefined class as
    fallback for unknown filters, globals, tests, object-attributes and -items.
    This way, most flaws and faults in view classes can be caught and affected
    areas can be ommited from the rendered output.
    """

    def __init__(self, undefined=Undefined, **kw):
        super(Environment, self).__init__(undefined=undefined, **kw)
        self.filters = defaultdict(self.undefined, self.filters)
        self.globals = defaultdict(self.undefined, self.globals)
        self.tests = defaultdict(self.undefined, self.tests)

    def handle_exception(self, *args, **kw):
        return self.undefined().__html__()

    def __getsth__(self, func, obj, name):
        try:
            return getattr(super(Environment, self), func)(obj, name)
        except BaseException:
            return self.undefined(obj, name)

    def getitem(self, obj, argument):
        return self.__getsth__('getitem', obj, argument)

    def getattr(self, obj, attribute):
        return self.__getsth__('getattr', obj, attribute)


@register_filter
def translate_url(url):
    if url is None:
        return None
    # XXX Is it really not possible to get to the actual template variables
    # (like context, view, request) through the jinja2 context?!??
    request = pyramid.threadlocal.get_current_request()
    if request is None:  # XXX should only happen in tests
        return url

    return url.replace("http://xml.zeit.de/", request.route_url('home'), 1)


@register_filter
def create_url(obj):
    if zeit.content.link.interfaces.ILink.providedBy(obj):
        return obj.url
    else:
        return translate_url(obj.uniqueId)


@register_filter
def format_date(obj, type='short'):
    formats = {'long': "d. MMMM yyyy, H:mm 'Uhr'",
               'short': "d. MMMM yyyy", 'short_num': "yyyy-MM-dd"}
    return format_datetime(obj, formats[type], locale="de_De")


@register_filter
def format_date_ago(dt, precision=2, past_tense='vor {}',
                    future_tense='in {}'):
    # customization of https://bitbucket.org/russellballestrini/ago :)
    delta = dt
    if not isinstance(dt, type(timedelta())):
        delta = datetime.now() - dt

    the_tense = past_tense
    if delta < timedelta(0):
        the_tense = future_tense

    delta = abs(delta)
    d = {
        'Jahr': int(delta.days / 365),
        'Tag': int(delta.days % 365),
        'Stunde': int(delta.seconds / 3600),
        'Minute': int(delta.seconds / 60) % 60,
        'Sekunde': delta.seconds % 60
    }
    hlist = []
    count = 0
    units = ('Jahr', 'Tag', 'Stunde', 'Minute', 'Sekunde')
    units_plural = {'Jahr': 'Jahren', 'Tag': 'Tagen', 'Stunde':
                    'Stunden', 'Minute': 'Minuten', 'Sekunde': 'Sekunden'}
    for unit in units:
        unit_displayed = unit
        if count >= precision:
            break  # met precision
        if d[unit] == 0:
            continue  # skip 0's
        if d[unit] != 1:
            unit_displayed = units_plural[unit]
        hlist.append('%s %s' % (d[unit], unit_displayed))
        count += 1
    human_delta = ', '.join(hlist)
    return the_tense.format(human_delta)


@register_filter
def obj_debug(value):
    try:
        res = []
        for k in dir(value):
            res.append('%r : %r;' % (k, getattr(value, k)))
        return '\n'.join(res)
    except AttributeError:
        return False


def strftime(t, format):
    """Return a string formatted version of a Python time representation. Can
    be either a time tuple, a time.struct_time or datetime.datetime instance.
    """
    try:
        if isinstance(t, time.struct_time) or isinstance(t, tuple):
            return time.strftime(format, t)
        elif isinstance(t, datetime):
            return t.strftime(format)
    except (AttributeError, TypeError, ValueError):
        pass
    return ''


@register_filter
def substring_from(string, find):
    return string.split(find)[-1]


@register_filter
def hide_none(string):
    if string is None:
        return ''
    else:
        return string


@register_filter
def remove_break(string):
    return re.sub('\n', '', string)


@register_filter
def replace_list_seperator(semicolonseperatedlist, seperator):
    return semicolonseperatedlist.replace(';', seperator)


# definition of default images sizes per layout context
default_images_sizes = {
    'default': (200, 300),
    'large': (800, 600),
    'small': (200, 300),
    'upright': (320, 480),
    'zmo-xl-header': (460, 306),
    'zmo-xl': (460, 306),
    'zmo-medium-left': (225, 125),
    'zmo-medium-center': (225, 125),
    'zmo-medium-right': (225, 125),
    'zmo-large-left': (225, 125),
    'zmo-large-center': (225, 125),
    'zmo-large-right': (225, 125),
    'zmo-small-left': (225, 125),
    'zmo-small-center': (225, 125),
    'zmo-small-right': (225, 125),
    '540x304': (290, 163),
    '940x400': (470, 200),
    '148x84': (74, 42),
    '220x124': (110, 62),
    '368x110': (160, 48),
    '368x220': (160, 96),
    '180x101': (90, 50),
    'zmo-landscape-large': (460, 306),
    'zmo-landscape-small': (225, 125),
    'zmo-square-large': (200, 200),
    'zmo-square-small': (50, 50),
    'zmo-lead-upright': (320, 480),
    'zmo-upright': (320, 432),
    'zmo-large': (460, 200),
    'zmo-medium': (330, 100),
    'zmo-small': (200, 50),
    'zmo-x-small': (100, 25),
    'zmo-card-picture': (320, 480),
    'og-image': (600, 315),
    'twitter-image_small': (120, 120),  # summary
    'twitter-image-large': (560, 300),  # summary_large_image, photo
}


@register_filter
def default_image_url(image,
                      image_pattern='default'):
    try:
        if image_pattern != 'default':
            width, height = default_images_sizes.get(image_pattern, (640, 480))
        elif hasattr(image, 'layout'):
            width, height = default_images_sizes.get(image.layout, (640, 480))
        else:
            width, height = default_images_sizes.get(image_pattern, (640, 480))
        # TODO: use secret from settings?
        signature = compute_signature(width, height, 'time')

        if image.uniqueId is None:
            return None

        scheme, netloc, path, query, fragment = urlparse.urlsplit(
            image.uniqueId)
        parts = path.split('/')
        parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
        path = '/'.join(parts)
        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        request = pyramid.threadlocal.get_current_request()

        return url.replace('http://xml.zeit.de/', request.route_url('home'), 1)
    except:
        log.debug('Cannot produce a default URL for %s', image)


@register_filter
def sharing_image_url(image_group,
                      image_pattern):
    sharing_image = closest_substitute_image(image_group, image_pattern)

    if not sharing_image:
        return

    return default_image_url(sharing_image, image_pattern)


def get_image_scales(scale_source):
    def to_int(value):
        return int(re.sub('[^0-9]', '', '0' + str(value)))

    if not scale_source:
        return
    try:
        fileobject = urllib2.urlopen(scale_source)
    except urllib2.URLError:
        return
    for scale in objectify.fromstring(fileobject.read()).iter():
        name = scale.attrib.get('name')
        width = to_int(scale.attrib.get('width'))
        height = to_int(scale.attrib.get('height'))
        yield name, (width, height)


@register_filter
def closest_substitute_image(image_group,
                             image_pattern,
                             force_orientation=False):
    """Returns the image from an image group, that most closely matches the
    target image pattern. Larger resolutions are always favored over smaller
    ones and the image orientation matching may be enforced.

    Usage as jinja filter:

        {{ my_image_group|closest_substitute_image('my-desired-pattern') }}

    :param image_group: Image Group instance that provides
                        zeit.content.image.interfaces.IImageGroup
    :param image_pattern: String representation of the target pattern ID.
    :param force_orientation: Boolean wether orientation of substitute image
                              must match that of target pattern.
    :returns: Unique ID of most suitable substitute image.
    """

    if not zeit.content.image.interfaces.IImageGroup.providedBy(image_group):
        return
    elif image_pattern in image_group:
        return image_group.get(image_pattern)

    # Determine the image size correlating to the provided pattern.
    s_size = (image_scales.get(image_pattern) or
              default_images_sizes.get(image_pattern))

    if not s_size:
        return

    orientation = lambda x, y: (x > y) << 1 | (x < y)  # Binary hashing

    # Aggregate a list of images from the image group with a target separator.
    candidates = [(image_pattern, s_size)]
    for name, img in image_group.items():
        size = img.getImageSize()
        if not force_orientation or orientation(*size) == orientation(*s_size):
            candidates.append((name, size))

    if len(candidates) == 1:
        return

    candidates = sorted(candidates, key=lambda i: i[1][0] * i[1][1])
    idx = candidates.index((image_pattern, s_size))
    candidates.pop(idx)

    # Select the candidate that is preferably one size larger than the target.
    return image_group.get(candidates[:idx + 1][-1][0])


@register_global
def get_teaser_template(block_layout,
                        content_type,
                        asset,
                        prefix='templates/inc/teaser/teaser_',
                        suffix='.html',
                        separator='_'):
    types = (block_layout, content_type, asset)
    default = ('default',)
    iterable = lambda t: isinstance(t, tuple) or isinstance(t, list)
    zipped = (t + default if iterable(t) else (t,) + default for t in types)

    combinations = [t for t in itertools.product(*zipped)]
    func = lambda x: '%s%s%s' % (prefix, separator.join(x), suffix)
    return map(func, combinations)


@register_global
def get_teaser_image(teaser_block, teaser, unique_id=None):
    import zeit.frontend.centerpage
    if unique_id:
        try:
            asset = zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            return None
    else:
        asset = zeit.frontend.centerpage.get_image_asset(teaser)
    if not zeit.content.image.interfaces.IImageGroup.providedBy(asset):
        return get_teaser_image(
            teaser_block, teaser,
            unique_id=zeit.frontend.template.default_teaser_images)
    asset_id = unique_id or asset.uniqueId
    image_base_name = re.split('/', asset.uniqueId.strip('/'))[-1]

    sample_image = asset.values().next()  # Assumes all images in this group
                                          # have the same mimetype.
    ext = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png'}.get(
        mimetypes.guess_type(sample_image.uniqueId)[0], 'jpg')

    image_id = '%s/%s-%s.%s' % \
        (asset_id, image_base_name, teaser_block.layout.image_pattern, ext)

    try:
        teaser_image = zope.component.getMultiAdapter(
            (asset, zeit.cms.interfaces.ICMSContent(image_id)),
            zeit.frontend.interfaces.ITeaserImage)
        return teaser_image
    except TypeError:
        # Don't fallback when an unique_id is given explicitly in order to
        # prevent infinite recursion.
        if unique_id:
            return None
        else:
            return get_teaser_image(
                teaser_block, teaser,
                unique_id=zeit.frontend.template.default_teaser_images)


@register_global
def create_image_url(teaser_block, image):
    image_pattern = teaser_block.layout.image_pattern
    image_url = default_image_url(
        image, image_pattern=image_pattern)
    return image_url


@register_filter
def get_image_metadata(image):
    try:
        image_metadata = zeit.content.image.interfaces.IImageMetadata(image)
        return image_metadata
    except TypeError:
        return None


class HTTPLoader(jinja2.BaseLoader):

    def __init__(self, url):
        self.url = url
        if url and not self.url.endswith('/'):
            self.url += '/'

    def get_source(self, environment, template):
        if not self.url:
            # XXX: Why doesn't this throw an exception?
            return (
                'ERROR: load_template_from_dav_url not configured',
                template, lambda: True)
        if self.url.startswith('egg://'):  # For tests
            parts = urlparse.urlparse(self.url)
            return (
                pkg_resources.resource_string(
                    parts.netloc, parts.path[1:] + template).decode('utf-8'),
                template, lambda: True)

        url = self.url + template
        log.debug('Loading template %r from %s', template, url)
        response = requests.get(url)
        return response.text, url, CompareModifiedHeader(
            url, response.headers.get('Last-Modified'))


class CompareModifiedHeader(object):
    """Compares a stored timestamp against the current Last-Modified header."""

    def __init__(self, url, timestamp):
        self.url = url
        self.last_retrieved = self.parse_rfc822(timestamp)

    def __call__(self):
        """Conforms to jinja2 uptodate semantics: Returns True if the template
        was not modified."""
        # NOTE: *Every time* a template is rendered we trigger an HTTP request.
        # Do we need introduce a delay to only perform the request every X
        # minutes?
        response = requests.head(self.url)
        last_modified = self.parse_rfc822(
            response.headers.get('Last-Modified'))
        return last_modified <= self.last_retrieved

    @staticmethod
    def parse_rfc822(timestamp):
        # XXX Dear stdlib, are you serious? Unfortunately, not even arrow
        # deals with RFC822 timestamps. This solution is sponsored by
        # <https://stackoverflow.com/questions/1568856>.
        if timestamp:
            return datetime.fromtimestamp(
                email.utils.mktime_tz(email.utils.parsedate_tz(timestamp)),
                pytz.utc)


class PrefixLoader(jinja2.BaseLoader):
    """Tweaked version of jinja2.PrefixLoader that defaults to prefix None
    if the requested path contains no prefix delimiter.
    """

    def __init__(self, mapping, delimiter='/'):
        self.mapping = mapping
        self.delimiter = delimiter

    def get_source(self, environment, template):
        if self.delimiter not in template:
            loader = self.mapping[None]
            name = template
        else:
            try:
                prefix, name = template.split(self.delimiter, 1)
                loader = self.mapping[prefix]
            except (ValueError, KeyError):
                raise jinja2.TemplateNotFound(template)
        try:
            return loader.get_source(environment, name)
        except jinja2.TemplateNotFound:
            # re-raise the exception with the correct fileame here.
            # (the one that includes the prefix)
            raise jinja2.TemplateNotFound(template)
