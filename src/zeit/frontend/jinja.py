from babel.dates import format_datetime
from repoze.bitblt.transform import compute_signature
from urlparse import urlsplit, urlunsplit
import itertools
import jinja2
import logging
import pyramid.threadlocal


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
