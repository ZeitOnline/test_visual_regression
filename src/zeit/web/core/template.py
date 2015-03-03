import datetime
import itertools
import logging
import mimetypes
import re
import time
import urlparse

import babel.dates
import pyramid.threadlocal
import repoze.bitblt.transform
import zope.component

import zeit.cms.interfaces
import zeit.content.link.interfaces
import zeit.content.cp.layout

import zeit.web
import zeit.web.core.comments
import zeit.web.core.interfaces


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
               'iso8601': "yyyy-MM-dd'T'HH:mm:ssZZZZZ"}
    # workaround for inadequate format_datetime() parsing
    # "yyyy-MM-dd'T'HH:mm:ssZZZZZ" or "yyyy-MM-dd'T'HH:mm:ssXXX" is not working
    if type == 'iso8601':
        try:
            return obj.replace(microsecond=0).isoformat()
        except AttributeError:
            return
    return babel.dates.format_datetime(obj, formats[type], locale="de_De")


@zeit.web.register_filter
def format_date_ago(dt, precision=2, past_tense='vor {}',
                    future_tense='in {}'):
    # customization of https://bitbucket.org/russellballestrini/ago :)
    delta = dt
    if not isinstance(dt, datetime.timedelta):
        delta = datetime.datetime.now() - dt

    the_tense = past_tense
    if delta < datetime.timedelta(0):
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
def get_teaser_layout(teaser_block):
    try:
        layout = teaser_block.layout.id
    except AttributeError:
        return 'default'

    try:
        serie = list(teaser_block)[0].serie
    except (AttributeError, IndexError, TypeError):
        serie = None

    if serie:
        layout = serie.column and 'zon-column' or 'zon-series'

    return zope.component.getUtility(
        zeit.web.core.interfaces.ITeaserMapping).get(layout, layout)


@zeit.web.register_filter
def remove_break(string):
    return re.sub('\n', '', string)


@zeit.web.register_filter
def replace_list_seperator(semicolonseperatedlist, seperator):
    return semicolonseperatedlist.replace(';', seperator)


@zeit.web.register_filter
def default_image_url(image, image_pattern='default'):
    try:
        scales = zope.component.getUtility(
            zeit.web.core.interfaces.IImageScales)
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
    target image pattern. Larger resolutions are always favored over smaller
    ones and the image orientation matching may be enforced.

    Usage as jinja filter:

        {{ my_image_group | closest_substitute_image('my-desired-pattern') }}

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

    # Determine the image scale correlating to the provided pattern.
    scale = zope.component.getUtility(
        zeit.web.core.interfaces.IImageScales).get(image_pattern)

    if not scale:
        return

    orientation = lambda x, y: (x > y) << 1 | (x < y)  # Binary hashing

    # Aggregate a list of images from the image group with a target separator.
    candidates = [(image_pattern, scale)]
    for name, img in image_group.items():
        size = img.getImageSize()
        if not force_orientation or orientation(*size) == orientation(*scale):
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
    return forms[min(len(forms) - 1, num - 1):][0] % num


@zeit.web.register_filter
def with_mods(elem, *mods):
    return ' '.join([elem] + ['%s--%s' % (elem, m) for m in mods])


@zeit.web.register_filter
def get_attr(*args):
    return getattr(*args)


@zeit.web.register_global
def get_teaser_commentcount(unique_id):
    thread = zeit.web.core.comments.get_thread(unique_id, just_count=True)
    if thread and thread.get('comment_count', 0) >= 5:
        return thread['comment_count']


@zeit.web.register_global
def topiclinks(centerpage):
    try:
        return zeit.web.core.interfaces.ITopicLink(centerpage)
    except TypeError:
        log.debug('object %s could not be adapted' % (
                  getattr(centerpage, 'uniqueId', '')))


@zeit.web.register_global
def get_teaser_template(block_layout,
                        content_type,
                        asset,
                        prefix='zeit.web.magazin:templates/inc/teaser/teaser_',
                        suffix='.html',
                        separator='_'):
    types = (block_layout, content_type, asset)
    default = ('default',)
    iterable = lambda t: isinstance(t, tuple) or isinstance(t, list)
    zipped = (t + default if iterable(t) else (t,) + default for t in types)

    combinations = [t for t in itertools.product(*zipped)]
    func = lambda x: '%s%s%s' % (prefix, separator.join(x), suffix)
    return map(func, combinations)


@zeit.web.register_global
def get_image_pattern(teaser_layout, orig_image_pattern):
    layout = zeit.content.cp.layout.TEASERBLOCK_LAYOUTS
    layout_image = {
        block.id: [block.image_pattern] for block in list(layout(None))}

    layout_image['zon-small'].extend(layout_image['leader'])
    layout_image['zon-parquet-small'].extend(layout_image['leader'])
    return layout_image.get(teaser_layout, [orig_image_pattern])


@zeit.web.register_global
def set_image_id(asset_id, image_base_name, image_pattern, ext):
    return '%s/%s-%s.%s' % (
        asset_id, image_base_name, image_pattern, ext)


def _existing_image(asset_id, image_base_name, image_patterns, ext):
    for image_pattern in image_patterns:
        image = set_image_id(asset_id, image_base_name, image_pattern, ext)
        try:
            return zeit.cms.interfaces.ICMSContent(image), image_pattern
        except:
            pass
    return None, None


@zeit.web.register_global
def get_column_image(teaser):
    try:
        return zeit.web.core.interfaces.ITeaserImage(
            teaser.authorships[0].target.column_teaser_image)
    except (AttributeError, TypeError):
        log.warn('Teaser {} has no authorships'.format(getattr(
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
    if len(asset.items()) == 0:
        return get_teaser_image(teaser_block, teaser, unique_id=default_id)

    # Assumes all images in this group have the same mimetype.
    sample_image = asset.values().next()

    ext = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png'}.get(
        mimetypes.guess_type(sample_image.uniqueId)[0], 'jpg')

    try:
        image_patterns = get_image_pattern(
            get_teaser_layout(teaser_block),
            teaser_block.layout.image_pattern)
    except AttributeError:
        return

    image, image_pattern = _existing_image(asset_id, image_base_name,
                                           image_patterns, ext)

    if image is None and image_pattern is None:
        image_pattern = teaser_block.layout.image_pattern
        image_id = set_image_id(asset_id, image_base_name, image_pattern, ext)
    else:
        image_id = image.uniqueId

    try:
        teaser_image = zope.component.getMultiAdapter(
            (asset, zeit.cms.interfaces.ICMSContent(image_id)),
            zeit.web.core.interfaces.ITeaserImage)
        teaser_image.image_pattern = image_pattern
        return teaser_image
    except TypeError:
        # Don't fallback when an unique_id is given explicitly in order to
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


@zeit.web.register_global
def get_google_tag_manager_host():
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get('google_tag_manager_host')
