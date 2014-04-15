from babel.dates import format_datetime
from datetime import datetime, timedelta
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
import zeit.frontend.centerpage


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


def format_date(obj, type='short'):
    formats = {'long': "dd. MMMM yyyy, H:mm 'Uhr'", 'short': "dd. MMMM yyyy"}
    return format_datetime(obj, formats[type], locale="de_De")


def format_date_ago(
        dt, precision=2, past_tense='vor {}', future_tense='in {}'):
    # customization of https://bitbucket.org/russellballestrini/ago :)
    delta = dt
    if type(dt) is not type(timedelta()):
        delta = datetime.now() - dt

    the_tense = past_tense
    if delta < timedelta(0):
        the_tense = future_tense

    delta = abs( delta )
    d = {
        'Jahr'   : int(delta.days / 365),
        'Tag'    : int(delta.days % 365),
        'Stunde'   : int(delta.seconds / 3600),
        'Minute' : int(delta.seconds / 60) % 60,
        'Sekunde' : delta.seconds % 60
    }
    hlist = []
    count = 0
    units = ( 'Jahr', 'Tag', 'Stunde', 'Minute', 'Sekunde' )
    units_plural = { 'Jahr':'Jahre', 'Tag':'Tage', 'Stunde':'Stunden', 'Minute':'Minuten', 'Sekunde':'Sekunden'}
    for unit in units:
        unit_displayed = unit
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        if d[ unit ] != 1:
            unit_displayed = units_plural[unit]
        hlist.append( '%s %s' % ( d[unit], unit_displayed ) )
        count += 1
    human_delta = ', '.join( hlist )
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

# definition of default images sizes per layout context
default_images_sizes = {
    'default': (200, 300),
    'large': (800, 600),
    'small': (200, 300),
    '540x304': (200, 300),
    'teaser_classic': (300, 169),
    'teaser_tile': (300, 300),
    'teaser_series_landscape': (640, 427),
    'teaser_series_square': (640, 640),
    'teaser_series_portrait': (640, 960),
    'teaser_column_dream': (640, 800),
    'teaser_column_snap_landscape': (640, 360),
    'teaser_column_snap_portrait': (640, 960),
    'hp_lead_square': (640, 640),
    'hp_lead_portrait': (640, 864),
    'hp_lead_superspecial': (980, 551),
}


def default_image_url(image,
                      image_pattern='default'):
    try:
        if hasattr(image, 'layout'):
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


def most_sufficient_teaser_tpl(block_layout,
                               content_type,
                               asset,
                               prefix='templates/inc/teaser/teaser_',
                               suffix='.html',
                               separator='_'):

    types = (block_layout, content_type, asset)
    defaults = ('default', 'default', 'default')
    zipped = zip(types, defaults)

    combinations = [t for t in itertools.product(*zipped)]
    func = lambda x: '%s%s%s' % (prefix, separator.join(x), suffix)
    return map(func, combinations)


def most_sufficient_teaser_image(teaser_block,
                                 teaser,
                                 asset_type=None,
                                 file_type='jpg'):
    image_pattern = teaser_block.layout.image_pattern
    if asset_type is None:
        asset = zeit.frontend.centerpage.auto_select_asset(teaser)
    elif asset_type == 'image':
        asset = zeit.frontend.centerpage.get_image_asset(teaser)
    else:
        raise KeyError(asset_type)
    if not zeit.content.image.interfaces.IImageGroup.providedBy(asset):
        return None
    image_base_name = re.split('/', asset.uniqueId)[-1]
    image_id = '%s/%s-%s.%s' % \
        (asset.uniqueId, image_base_name, image_pattern, file_type)
    try:
        teaser_image = zeit.cms.interfaces.ICMSContent(image_id)
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
                    parts.netloc, parts.path[1:] + template),
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
