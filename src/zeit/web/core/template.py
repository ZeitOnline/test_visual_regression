import datetime
import itertools
import logging
import mimetypes
import re
import time
import types
import urllib
import urlparse
import jinja2
import babel.dates
import pyramid.threadlocal
import repoze.bitblt.transform
import zope.component
import zope.component.interfaces

import zeit.cms.interfaces
import zeit.content.link.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.layout

import zeit.web
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.utils

log = logging.getLogger(__name__)


@zeit.web.register_filter
def translate_url(url):
    if url is None:
        return
    # XXX Is it really not possible to get to the actual template variables
    # (like context, view, request) through the jinja2 context?!??
    request = pyramid.threadlocal.get_current_request()
    if request is None:  # XXX should only happen in tests
        return url

    return url.replace('http://xml.zeit.de/', request.route_url('home'), 1)


@zeit.web.register_filter
def create_url(obj):
    if zeit.content.link.interfaces.ILink.providedBy(obj):
        return obj.url
    else:
        return translate_url(obj.uniqueId)


@zeit.web.register_filter
def format_date(obj, type='short'):
    formats = {'long': "d. MMMM yyyy, H:mm 'Uhr'",
               'short': "d. MMMM yyyy", 'short_num': "yyyy-MM-dd",
               'iso8601': "yyyy-MM-dd'T'HH:mm:ssZZZZZ",
               'time_only': "HH:mm 'Uhr'"}
    # workaround for inadequate format_datetime() parsing
    # "yyyy-MM-dd'T'HH:mm:ssZZZZZ" or "yyyy-MM-dd'T'HH:mm:ssXXX" is not working
    if type == 'iso8601':
        try:
            return obj.replace(microsecond=0).isoformat()
        except AttributeError:
            return
    return babel.dates.format_datetime(obj, formats[type], locale="de_De")


@zeit.web.register_filter
def obj_debug(value):
    try:
        res = []
        for k in dir(value):
            res.append('%r : %r;' % (k, getattr(value, k)))
        return '\n'.join(res)
    except AttributeError:
        return False


@zeit.web.register_filter
def strftime(t, format):
    """Return a string formatted version of a Python time representation. Can
    be either a time tuple, a time.struct_time or datetime.datetime instance.
    """
    try:
        if isinstance(t, time.struct_time) or isinstance(t, tuple):
            return time.strftime(format, t)
        elif isinstance(t, datetime.datetime):
            return t.strftime(format)
    except (AttributeError, TypeError, ValueError):
        return


@zeit.web.register_filter
def substring_from(string, find):
    return string.split(find)[-1]


@zeit.web.register_filter
def hide_none(string):
    if string is None:
        return ''
    else:
        return string


@zeit.web.register_filter
def get_layout(block, request=None):
    # Calculating the layout of a cp block can be slightly more expensive in
    # zeit.web, since we do lookups in some vocabularies, to change the layout,
    # that was originally set for the block.
    # Since we might lookup a layout more than once per request, we can cache
    # it in the request object.

    request = request or pyramid.threadlocal.get_current_request()

    try:
        key = request and hash(block)
    except (NotImplementedError, TypeError), e:
        log.debug('Cannot cache {} layout: {}'.format(block, e))
        key = None

    if key:
        request.teaser_layout = getattr(request, 'teaser_layout', None) or {}
        layout = request.teaser_layout.get(key, None)
        if layout:
            return layout

    try:
        layout_id = block.layout.id
    except (AttributeError, TypeError):
        layout_id = 'hide'

    try:
        teaser = list(block)[0]
    except (IndexError, TypeError):
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(block):
            layout = layout_id
        else:
            layout = 'hide'
    else:
        if isinstance(teaser, zeit.cms.syndication.feed.FakeEntry):
            log.debug('Broken ref at {}'.format(teaser.uniqueId))
            layout = 'hide'
        elif False:
            # XXX What about placeholder containers?
            layout = 'hide'
        elif getattr(teaser, 'serie', None):
            layout = 'zon-series'
            if teaser.serie.column and get_column_image(teaser):
                layout = 'zon-column'
        elif getattr(teaser, 'blog', None):
            layout = 'zon-blog'
        else:
            layout = layout_id

    layout = zope.component.getUtility(
        zeit.web.core.interfaces.ITeaserMapping).get(layout, layout)

    if key:
        request.teaser_layout[key] = layout

    return layout


@zeit.web.register_filter
def first_child(iterable):
    try:
        return iter(iterable).next()
    except:
        return


@zeit.web.register_filter
def remove_break(string):
    return re.sub('\n', '', string)


@zeit.web.register_filter
def replace_list_seperator(scsv, seperator):
    return scsv.replace(';', seperator)


# definition of default images sizes per layout context
scales = {
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
    '580x148': (290, 163),
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
    'zmo-print-cover': (315, 424),
    'og-image': (600, 315),
    'twitter-image_small': (120, 120),  # summary
    'twitter-image-large': (560, 300),  # summary_large_image, photo
    'newsletter-540x304': (540, 304),
    'newsletter-220x124': (220, 124),
    'zon-thumbnail': (580, 326),
    'zon-large': (580, 326),
    'zon-article-large': (820, 462),
    'zon-printbox': (320, 234),
    'zon-printbox-wide': (320, 148),
    'zon-topic': (980, 418),
    'zon-column': (300, 400),
    'brightcove-still': (580, 326),
    'brightcove-thumbnail': (120, 67),
    'spektrum': (220, 124)
}


@zeit.web.register_filter
def default_image_url(image, image_pattern='default'):
    try:
        image_pattern = getattr(image, 'image_pattern', image_pattern)
        if image_pattern != 'default':
            width, height = scales.get(image_pattern, (640, 480))
        elif hasattr(image, 'layout'):
            width, height = scales.get(image.layout, (640, 480))
        else:
            width, height = scales.get(image_pattern, (640, 480))
        # TODO: use secret from settings?
        signature = repoze.bitblt.transform.compute_signature(
            width, height, 'time')

        if getattr(image, 'uniqueId', None) is None:
            return

        scheme, netloc, path, query, fragment = urlparse.urlsplit(
            image.uniqueId)
        parts = path.split('/')
        parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
        path = '/'.join(parts)
        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        request = pyramid.threadlocal.get_current_request()

        return url.replace('http://xml.zeit.de/', request.route_url('home'), 1)
    except Exception, e:
        # XXX: Surely we do not want to try-except on a function scope.
        log.debug('Cannot produce a default URL for {}. Reason {}'.format(
                  image, e))


@zeit.web.register_filter
def sharing_image_url(image_group,
                      image_pattern):
    sharing_image = closest_substitute_image(image_group, image_pattern)

    if not sharing_image:
        return

    return default_image_url(sharing_image, image_pattern)


@zeit.web.register_filter
def closest_substitute_image(image_group,
                             image_pattern,
                             force_orientation=False):
    """Returns the image from an image group, that most closely matches the
    target image pattern (while ignoring the master image). Larger resolutions
    are always favored over smaller ones and the image orientation matching may
    be enforced.

    Usage as jinja filter:

        {{ my_image_group | closest_substitute_image('my-desired-pattern') }}

    :param image_group: Image Group instance that provides
                        zeit.content.image.interfaces.IImageGroup
    :param image_pattern: String representation of the target pattern ID.
    :param force_orientation: Boolean wether orientation of substitute image
                              must match that of target pattern.
    :returns: Unique ID of most suitable substitute image.
    """

    # make sure it's an Image Group
    if not zeit.content.image.interfaces.IImageGroup.providedBy(image_group):
        return
    elif image_pattern in image_group:
        # return happily if image_pattern is present
        return image_group.get(image_pattern)

    # Determine the image scale correlating to the provided pattern.
    scale = zope.component.getUtility(
        zeit.web.core.interfaces.IImageScales).get(image_pattern)

    if not scale:
        return

    def orientation(x, y):
        return (x > y) << 1 | (x < y)  # Binary hashing

    # Aggregate a list of images from the image group with a target separator.
    candidates = [(image_pattern, scale)]
    for name, img in image_group.items():
        size = img.getImageSize()
        if image_group.master_image != name and (
                not force_orientation or
                orientation(*size) == orientation(*scale)):
            candidates.append((name, size))

    if len(candidates) == 1:
        return

    candidates = sorted(candidates, key=lambda i: i[1][0] * i[1][1])
    idx = candidates.index((image_pattern, scale))
    candidates.pop(idx)

    # Select the candidate that is preferably one size larger than the target.
    return image_group.get(candidates[:idx + 1][-1][0])


@zeit.web.register_filter
def pluralize(num, *forms):
    try:
        num = int(num)
    except ValueError:
        num = 0
    return forms[min(len(forms) - 1, num):][0].format(num)


@zeit.web.register_filter
def with_mods(b_or_e, *mods):
    """Decorate a BEM-style block or element with an a set of modifiers."""
    return ' '.join([b_or_e] + ['{}--{}'.format(b_or_e, m) for m in
                                set(mods) if isinstance(m, basestring)])


@zeit.web.register_filter
def get_attr(*args):
    return getattr(*args)


@zeit.web.register_filter
def topic_links(centerpage):
    try:
        return zeit.web.core.interfaces.ITopicLink(centerpage)
    except TypeError:
        log.debug('object %s could not be adapted' % (
                  getattr(centerpage, 'uniqueId', '')))


@jinja2.contextfilter
def call_macro_by_name(context, macro_name, *args, **kwargs):
    return context.vars[macro_name](*args, **kwargs)


@zeit.web.register_global
def get_teaser_template(block_layout,
                        content_type,
                        asset,
                        prefix='zeit.web.magazin:templates/inc/teaser/teaser_',
                        suffix='.html',
                        separator='_'):
    types = (block_layout, content_type, asset)
    default = ('default',)

    def iterable(t):
        return isinstance(t, tuple) or isinstance(t, list)

    zipped = (t + default if iterable(t) else (t,) + default for t in types)

    combinations = [t for t in itertools.product(*zipped)]
    return map(lambda x: '%s%s%s' % (prefix, separator.join(x), suffix),
               combinations)


@zeit.web.register_global
def get_image_pattern(teaser_layout, orig_image_pattern):
    layout = zeit.content.cp.layout.TEASERBLOCK_LAYOUTS
    layout_image = {block.id: [block.image_pattern] for block in
                    list(layout(None)) if block.image_pattern}

    layout_image['zon-small'].extend(layout_image['leader'])
    layout_image['zon-parquet-small'].extend(layout_image['leader'])
    layout_image['zon-parquet-large'].extend(layout_image['leader'])
    return layout_image.get(teaser_layout, [orig_image_pattern])


@zeit.web.register_global
def set_image_id(asset_id, image_base_name, image_pattern, ext):
    return '%s/%s-%s.%s' % (
        asset_id, image_base_name, image_pattern, ext)


def _existing_image(asset_id, base_name, patterns, ext, filenames):
    possible_filenames = set(["{}-{}.{}".format(
        base_name, pattern, ext) for pattern in patterns])

    try:
        name = possible_filenames.intersection(filenames).pop()
        pattern = name.replace('{}-'.format(base_name), '')
        pattern = pattern.replace('.{}'.format(ext), '')
        name = "{}{}".format(asset_id, name)

        return zeit.cms.interfaces.ICMSContent(name), pattern
    except:
        pass

    return None, None


@zeit.web.register_global
def get_column_image(teaser):
    try:
        image_group = teaser.authorships[0].target.image_group
        image = closest_substitute_image(image_group, 'zon-column')
        return zeit.web.core.interfaces.ITeaserImage(image)
    except (AttributeError, IndexError, TypeError):
        log.debug('Author of {} has no column image.'.format(getattr(
            teaser, 'uniqueId', 'unknown')))


@zeit.web.register_global
def get_teaser_image(teaser_block, teaser, unique_id=None):
    import zeit.web.core.centerpage

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    default_id = conf.get('default_teaser_images')

    if unique_id:
        try:
            asset = zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            return
    else:
        asset = zeit.web.core.centerpage.get_image_asset(teaser)

    # If the asset is not an image group, restart with default image.
    if not zeit.content.image.interfaces.IImageGroup.providedBy(asset):
        return get_teaser_image(teaser_block, teaser, unique_id=default_id)

    asset_id = unique_id or asset.uniqueId
    image_base_name = re.split('/', asset.uniqueId.strip('/'))[-1]

    # If imagegroup has no images, return default image
    if len(asset) == 0:
        return get_teaser_image(teaser_block, teaser, unique_id=default_id)

    # Assumes all images in this group have the same mimetype.
    filenames = asset.keys()
    sample_image = u'{}{}'.format(asset.uniqueId, filenames[0])

    ext = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png'}.get(
        mimetypes.guess_type(sample_image)[0], 'jpg')

    try:
        image_patterns = get_image_pattern(
            get_layout(teaser_block),
            teaser_block.layout.image_pattern)
    except AttributeError:
        return

    image, image_pattern = _existing_image(asset_id, image_base_name,
                                           image_patterns, ext, filenames)

    try:
        if image is None and image_pattern is None:

            image_pattern = teaser_block.layout.image_pattern
            image_id = set_image_id(asset_id, image_base_name,
                                    image_pattern, ext)
            image = zeit.cms.interfaces.ICMSContent(image_id)

        teaser_image = zope.component.getMultiAdapter(
            (asset, image),
            zeit.web.core.interfaces.ITeaserImage)
        teaser_image.image_pattern = image_pattern
        return teaser_image
    except TypeError:
        log.debug('Cannot retrieve teaser image: {}'.format(image_id))
        # Don't fallback when a unique_id is given explicitly in order to
        # prevent infinite recursion.
        if not unique_id:
            return get_teaser_image(teaser_block, teaser, unique_id=default_id)


@zeit.web.register_global
def create_image_url(teaser_block, image):
    image_pattern = teaser_block.layout.image_pattern
    image_url = default_image_url(
        image, image_pattern=image_pattern)
    return image_url


@zeit.web.register_filter
def get_image_metadata(image):
    try:
        return zeit.content.image.interfaces.IImageMetadata(image)
    except TypeError:
        return


@zeit.web.register_filter
def get_repository_image(image):
    base_image = zeit.web.core.block.BaseImage()
    base_image.image = image
    base_image.uniqueId = image.uniqueId
    return base_image


@zeit.web.register_filter
def get_image_group(asset):
    try:
        return zeit.content.image.interfaces.IImageGroup(asset)
    except TypeError:
        return


@zeit.web.register_filter
def get_module(module, name=None):
    return zeit.web.core.utils.get_named_adapter(
        module, zeit.edit.interfaces.IBlock, 'cpextra')


@zeit.web.register_filter
def get_area(area, name=None):
    return zeit.web.core.utils.get_named_adapter(
        area, zeit.content.cp.interfaces.IRenderedArea, 'kind')


@zeit.web.register_filter
def attr_safe(text):
    """ Return an attribute safe version of text """
    return re.sub('[^a-zA-Z]', '', text).lower()


@zeit.web.register_global
def get_google_tag_manager_host():
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get('google_tag_manager_host')


@zeit.web.register_global
def list(iterable):
    return types.ListType(iterable)


@zeit.web.register_global
def tuple(iterable):
    return types.TupleType(iterable)


@zeit.web.register_global
def dict(mapping):
    return types.DictType(mapping)


@zeit.web.register_global
def debug_breaking_news():
    request = pyramid.threadlocal.get_current_request()
    return 'eilmeldung' == request.GET.get('debug', '')


@zeit.web.register_global
def calculate_pagination(current_page, total_pages, slots=7):
    # only accept ints as params
    if not (isinstance(current_page, int) and isinstance(total_pages, int)):
        return
    # check for sensible values
    if current_page > total_pages or current_page < 0 or total_pages <= 1:
        return

    # we have 7 slots by default to display pages,
    # so anything less than 8 pages can be displayed 'as is'
    if total_pages <= slots:
        return range(1, total_pages + 1)

    # collect all known page numbers:
    #  - first and last page
    #  - current page and its two neighbours
    locp = max(1, current_page - 1)  # left of current page
    rocp = min(total_pages, current_page + 1)  # left of current page
    pages_set = set([1, locp, current_page, rocp, total_pages])
    pages = sorted(list(pages_set))

    # fill up slots with number or ellipsis
    if pages[1] - pages[0] == 2:
        pages.insert(1, pages[0] + 1)
    elif pages[1] - pages[0] > 2:
        pages.insert(1, None)

    if pages[-1] - pages[-2] == 2:
        pages.insert(-1, pages[-2] + 1)
    elif pages[-1] - pages[-2] > 2:
        pages.insert(-1, None)

    # account for edge cases where's more to fill
    if len(pages) < slots:
        pre_none_filler = range(min(total_pages, current_page + 2),
                                total_pages)[:slots - len(pages)]
        post_none_filler = range(2,
                                 max(2, current_page - 1))[len(pages) - slots:]

        if pre_none_filler:
            pages = pages[:-2] + pre_none_filler + pages[-2:]
        if post_none_filler:
            pages = pages[:2] + post_none_filler + pages[2:]

    return pages


@zeit.web.register_filter
def append_get_params(request, **kw):
    # Append GET parameters that are not reset
    # by setting the param value to None explicitly.
    def encode(value):
        return unicode(value).encode('utf-8')

    params = [(encode(k), encode(v)) for k, v in itertools.chain(
              (i for i in request.GET.iteritems() if i[0] not in kw),
              (i for i in kw.iteritems() if i[1] is not None))]

    if params == []:
        return request.path_url
    return '?'.join([request.path_url, urllib.urlencode(params)])


@zeit.web.register_filter
def remove_get_params(url, *args):
    # ToDo: This should be used in templates,
    # if append_get_params gets refactored.
    # It'd be more useful to use these functions on URL and not request level
    # This way we could say sth. like
    # `request | make_url() |
    #  append_get_param(foo='ba', ba='batz') | remove_get_param('foobar')`
    # and vice versa.

    scheme, netloc, path, query, frag = urlparse.urlsplit(url)
    query_p = urlparse.parse_qs(query)
    for arg in args:
        query_p.pop(arg, None)

    return '{}://{}{}?{}'.format(
        scheme, netloc, path, urllib.urlencode(query_p, doseq=True))
