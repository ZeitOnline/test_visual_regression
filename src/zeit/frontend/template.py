from babel.dates import format_datetime
from datetime import datetime, timedelta
from lxml import objectify
from repoze.bitblt.transform import compute_signature
from urlparse import urlsplit, urlunsplit
import email.utils
import itertools
import jinja2
import logging
import pkg_resources
import pyramid.threadlocal
import pytz
import re
import requests
import urlparse
import zeit.cms.interfaces
import zeit.content.link.interfaces
import zeit.frontend.centerpage
import zope.component

log = logging.getLogger(__name__)


@jinja2.contextfilter
def translate_url(context, url):
    if url is None:
        return None
    # XXX Is it really not possible to get to the actual template variables
    # (like context, view, request) through the jinja2 context?!??
    request = pyramid.threadlocal.get_current_request()
    if request is None:  # XXX should only happen in tests
        return url

    return url.replace("http://xml.zeit.de/", request.route_url('home'), 1)


@jinja2.contextfilter
def create_url(context, obj):
    if zeit.content.link.interfaces.ILink.providedBy(obj):
        return obj.url
    else:
        return translate_url(context, obj.uniqueId)


def format_date(obj, type='short'):
    formats = {'long': "d. MMMM yyyy, H:mm 'Uhr'", 'short': "d. MMMM yyyy"}
    return format_datetime(obj, formats[type], locale="de_De")


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


def obj_debug(value):
    try:
        res = []
        for k in dir(value):
            res.append('%r : %r;' % (k, getattr(value, k)))
        return '\n'.join(res)
    except AttributeError:
        return False


def substring_from(string, find):
    return string.split(find)[-1]


def hide_none(string):
    if string is None:
        return ''
    else:
        return string


def replace_list_seperator(semicolonseperatedlist, seperator):
    return semicolonseperatedlist.replace(';', seperator)


def _get_navigation():
    navigation = pkg_resources.resource_filename(
        __name__, 'data/navigation.xml')
    tree = objectify.parse(navigation)
    root = tree.getroot()
    top_formate = root.xpath('list[@id="top-formate"]')[0]
    sitemap = root.xpath('list[@id="sitemap"]')[0]
    return top_formate, sitemap

top_formate, sitemap = _get_navigation()
del _get_navigation


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
    'twitter-image': (590, 295),
}


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

        scheme, netloc, path, query, fragment = urlsplit(image.uniqueId)
        parts = path.split('/')
        parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
        path = '/'.join(parts)
        url = urlunsplit((scheme, netloc, path, query, fragment))
        request = pyramid.threadlocal.get_current_request()

        return url.replace("http://xml.zeit.de/", request.route_url('home'), 1)
    except:
        log.debug('Cannot produce a default URL for %s', image)


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


def get_teaser_image(teaser_block, teaser):
    asset = zeit.frontend.centerpage.get_image_asset(teaser)
    if not zeit.content.image.interfaces.IImageGroup.providedBy(asset):
        return None

    image_base_name = re.split('/', asset.uniqueId.strip('/'))[-1]
    image_id = '%s/%s-%s.jpg' % \
        (asset.uniqueId, image_base_name, teaser_block.layout.image_pattern)
    try:
        teaser_image = zope.component.getMultiAdapter(
            (asset, zeit.cms.interfaces.ICMSContent(image_id)),
            zeit.frontend.interfaces.ITeaserImage)
        return teaser_image
    except TypeError:
        return None


def create_image_url(teaser_block, image):
    image_pattern = teaser_block.layout.image_pattern
    image_url = default_image_url(
        image, image_pattern=image_pattern)
    return image_url


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
