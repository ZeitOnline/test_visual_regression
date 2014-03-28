from babel.dates import format_datetime
from datetime import datetime
from repoze.bitblt.transform import compute_signature
from urlparse import urlsplit, urlunsplit
import email.utils
import itertools
import jinja2
import logging
import pyramid.threadlocal
import pytz
import requests


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


def format_date(obj, type):
    format = ""
    if type == 'long':
        format = "dd. MMMM yyyy, H:mm 'Uhr'"
    elif type == 'short':
        format = "dd. MMMM yyyy"
    return format_datetime(obj, format, locale="de_De")


def replace_list_seperator(semicolonseperatedlist, seperator):
    return semicolonseperatedlist.replace(';', seperator)

# definition of default images sizes per layout context
default_images_sizes = dict(
    large=(800, 600),
    small=(200, 300),
)


def default_image_url(image):
    try:
        width, height = default_images_sizes.get(image.layout, (640, 480))
        # TODO: use secret from settings?
        signature = compute_signature(width, height, 'time')

        if image.src is None:
            return None

        scheme, netloc, path, query, fragment = urlsplit(image.src)
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

        url = self.url + template
        response = requests.get(url)
        return response.text, template, CompareModifiedHeader(
            url, response.headers.get('Last-Modified'))


class CompareModifiedHeader(object):
    """Compares a stored timestamp against the current Last-Modified header."""

    def __init__(self, url, timestamp):
        self.url = url
        self.last_retrieved = self.parse_rfc822(timestamp)

    def __call__(self):
        """Conforms to jinja2 uptodate semantics: Returns True if the template
        was not modified."""
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
