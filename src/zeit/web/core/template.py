# coding: utf8
import collections
import datetime
import itertools
import logging
import mimetypes
import random
import re
import time
import types
import urllib
import urlparse

import babel.dates
import pyramid.threadlocal
import repoze.bitblt.transform
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces
import zeit.magazin.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.image
import zeit.web.core.interfaces
import zeit.web.core.utils

log = logging.getLogger(__name__)


@zeit.web.register_global
def get_variant(group, variant_id):
    try:
        variant = zeit.web.core.image.VARIANT_SOURCE.factory.find(
            group, variant_id)
    except TypeError, err:
        log.debug(err.message)
    except KeyError:
        log.debug(u'No {} variant for {}'.format(variant_id, group.uniqueId))
    else:
        variant.__parent__ = group
        try:
            return zeit.web.core.interfaces.ITeaserImage(variant)
        except TypeError:
            return None


@zeit.web.register_global
def get_image(module=None, content=None, fallback=True, variant_id=None,
              default='default'):
    """Universal image retrieval function to be used in templates.

    :param module: Module to extract a content and layout from
    :param content: Override to provide different content with image reference
    :param fallback: Specify whether missing images should render a fallback
    :param variant_id: Override for automatic variant determination
    :param default: If variant_id is None, specify a default for automatic
                    variant determination
    """

    if content is None:
        content = first_child(module)

    try:
        group = zeit.content.image.interfaces.IImages(content).image
    except (TypeError, AttributeError):
        group = None

    try:
        if group is None:
            group = module.image
    except (TypeError, AttributeError):
        pass

    if not zeit.content.image.interfaces.IImageGroup.providedBy(group):
        if not fallback:
            return None

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        default_id = conf.get('default_teaser_images')
        group = zeit.cms.interfaces.ICMSContent(default_id, None)

    if zeit.web.core.interfaces.IFrontendBlock.providedBy(module):
        layout = module
    else:
        layout = zeit.content.cp.layout.get_layout(get_layout(module))

    if variant_id is None:
        try:
            variant_id = layout.image_pattern
        except AttributeError:
            variant_id = default

    return get_variant(group, variant_id)


@zeit.web.register_test
def variant(image):
    # TRASHME: Jinja test to distinguish between bitblt/zci images.
    return isinstance(image, zeit.web.core.image.VariantImage)


@zeit.web.register_test
def zmo_content(content):
    # XXX Stopgap until longforms are not IZMOContent anymore (ZON-2411).
    return not getattr(content, 'uniqueId', '').replace(
        zeit.cms.interfaces.ID_NAMESPACE, '', 1).startswith('feature') and (
            zeit.magazin.interfaces.IZMOContent.providedBy(content))


@zeit.web.register_test
def zett_content(content):
    return zeit.content.link.interfaces.ILink.providedBy(
        content) and content.url.startswith('http://ze.tt')


@zeit.web.register_test
def column(context):
    return context.serie and context.serie.column


@zeit.web.register_test
def leserartikel(context):
    return getattr(context, 'genre', None) and context.genre == 'leserartikel'


@zeit.web.register_filter
def block_type(obj):
    """Outputs the class name in lower case format of one or multiple block
    elements.

    :param obj: list, str or tuple
    :rtype: list, str or tuple
    """

    if obj is None:
        return 'no_block'
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return obj.__class__(block_type(o) for o in obj)
    else:
        return getattr(obj, '__block__', type(obj).__name__.lower())


@zeit.web.register_ctxfilter
def create_url(context, obj, request=None):
    try:
        req = request or context.get('view').request  # See zwc.decorator
        host = req.route_url('home')
    except:
        log.debug('Could not retrieve request from context: %s' % obj)
        host = '/'

    if isinstance(obj, basestring):
        return obj.replace(
            zeit.cms.interfaces.ID_NAMESPACE, host, 1).replace('.cp2015', '')
    elif zeit.content.link.interfaces.ILink.providedBy(obj):
        return obj.url
    elif zeit.content.video.interfaces.IVideo.providedBy(obj):
        slug = zeit.web.site.view_video.Video.get_slug(obj)
        # titles = (t for t in (obj.supertitle, obj.title) if t)
        # slug = zeit.cms.interfaces.normalize_filename(u' '.join(titles))
        return create_url(
            context, u'{}/{}'.format(obj.uniqueId, slug), request)
    elif zeit.cms.interfaces.ICMSContent.providedBy(obj):
        return create_url(context, obj.uniqueId, request=request)
    else:
        return ''


@zeit.web.register_ctxfilter
def append_campaign_params(context, url):
    # add campaign parameters for linked ze.tt content
    if url is not None and url.startswith('http://ze.tt'):
        try:
            kind = context.get('area').kind
        except:
            kind = None

        if kind == 'zett':
            campaign_params = {
                'utm_campaign': 'zonparkett',
                'utm_medium': 'parkett',
                'utm_source': 'zon'}
        else:
            campaign_params = {
                'utm_campaign': 'zonteaser',
                'utm_medium': 'teaser',
                'utm_source': 'zon'}

        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        query_params = urlparse.parse_qs(query)
        query_params.update(campaign_params)
        # sort query params alphabetical by key for SEO
        return '{}://{}{}?{}'.format(scheme, netloc, path, urllib.urlencode(
            collections.OrderedDict(sorted(query_params.items())), doseq=True))
    else:
        return url


@zeit.web.register_filter
def format_date(date, type='short', pattern=None):
    if date is None:
        return ''
    formats = {'long': "d. MMMM yyyy, H:mm 'Uhr'",
               'regular': "d. MMMM yyyy, H:mm",
               'short': "d. MMMM yyyy",
               'short_num': "yyyy-MM-dd",
               'iso8601': "yyyy-MM-dd'T'HH:mm:ssZZZZZ",
               'time_only': "HH:mm 'Uhr'"}
    # workaround for inadequate format_datetime() parsing
    # "yyyy-MM-dd'T'HH:mm:ssZZZZZ" or "yyyy-MM-dd'T'HH:mm:ssXXX" is not working
    if type == 'iso8601':
        try:
            return date.replace(microsecond=0).isoformat()
        except AttributeError:
            return
    elif type == 'timedelta':
        delta = date - datetime.datetime.now(date.tzinfo)
        text = babel.dates.format_timedelta(delta, threshold=1,
                                            add_direction=True, locale="de_DE")
        return text[:1].lower() + text[1:] if text else ''
    if pattern is None:
        pattern = formats[type]
    # adjust UTC dates to local time
    if date.tzinfo:
        tz = babel.dates.get_timezone('Europe/Berlin')
        date = date.astimezone(tz)
    return babel.dates.format_datetime(date, pattern, locale="de_DE")


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
def get_layout(block, request=None):
    # Calculating the layout of a cp block can be slightly more expensive in
    # zeit.web, since we do lookups in some vocabularies, to change the layout,
    # that was originally set for the block.
    # Since we might lookup a layout more than once per request, we can cache
    # it in the request object.

    # XXX This filter is in desperate need of a major overhaul!

    request = request or pyramid.threadlocal.get_current_request()

    try:
        key = request and hash(block)
    except (NotImplementedError, TypeError), e:
        log.debug('Cannot cache {} layout: {}'.format(type(block), e))
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
        layout = layout_id
        if layout == 'zon-square':
            # ToDo: Remove when Longform will be generally used on www.zeit.de
            if urlparse.urlparse(teaser.uniqueId).path.startswith('/feature/'):
                layout = layout
            elif zeit.magazin.interfaces.IZMOContent.providedBy(teaser):
                layout = 'zmo-square'
        # XXX Instead of hard-coding a layout change here, we should make use
        # of z.w.core.centerpage.dispatch_teaser_via_contenttype() and
        # register a specific teaser module for authors.
        elif (zeit.content.author.interfaces.IAuthor.providedBy(teaser) and
                layout == 'zon-small' and
                block.__parent__.kind in ['duo', 'minor']):
            layout = 'zon-author'

    layout = zeit.web.core.centerpage.TEASER_MAPPING.get(layout, layout)

    if key:
        request.teaser_layout[key] = layout

    return layout


@zeit.web.register_filter
def get_journalistic_format(block):
    source = zeit.content.cp.layout.TEASERBLOCK_LAYOUTS.factory._get_tree()

    def allowed(layout_id):
        try:
            xpath = '/layouts/layout[@id="{}"]/@areas'.format(layout_id)
            return block.__parent__.kind in source.xpath(xpath)[0].split(' ')
        except (AttributeError, IndexError):
            return

    if not (allowed('zon-series') or allowed('zon-column') or
            allowed('zon-blog')):
        return

    try:
        teaser = list(block)[0]
    except (IndexError, TypeError):
        return

    if getattr(teaser, 'serie', None):
        if teaser.serie.column:
            return 'column'
        else:
            return 'series'
    elif getattr(teaser, 'blog', None):
        return 'blog'


@zeit.web.register_filter
def first_child(iterable):
    try:
        return iter(iterable).next()
    except:
        return


@zeit.web.register_filter
def first_ancestor(iterable):
    child = first_child(iterable)
    if child is None:
        return iterable
    return first_ancestor(child)


@zeit.web.register_filter
def startswith(string, value):
    if isinstance(string, basestring):
        return string.startswith(value)
    return False


@zeit.web.register_filter
def remove_break(string):
    if isinstance(string, basestring):
        return re.sub('\n', '', string)
    return string


@zeit.web.register_filter
def is_gallery(context):
    return zeit.content.gallery.interfaces.IGallery.providedBy(context)


@zeit.web.register_filter
def is_video(context):
    return zeit.content.video.interfaces.IVideo.providedBy(context)


@zeit.web.register_filter
def is_liveblog(context):
    return zeit.content.article.interfaces.IArticle.providedBy(
        context) and context.template == 'zon-liveblog'


# TRASHME: Definition of default images sizes for bitblt images
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
    'zon-column': (300, 400),
    'zon-square': (460, 460),
    'topic': (980, 418),
    'brightcove-still': (580, 326),
    'brightcove-thumbnail': (120, 67),
    'spektrum': (220, 124)
}


@zeit.web.register_filter
def default_image_url(image, image_pattern='default'):
    # TRASHME: Creates image urls for bitblt images
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
        if zeit.web.core.image.is_image_expired(image):
            return

        scheme, netloc, path, query, fragment = urlparse.urlsplit(
            image.uniqueId)
        parts = path.split('/')
        parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
        path = '/'.join(parts)
        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        request = pyramid.threadlocal.get_current_request()

        return url.replace('http://xml.zeit.de', request.image_host, 1)
    except Exception, e:
        # XXX: Surely we do not want to try-except on a function scope.
        log.debug('Cannot produce a default URL for {}. Reason {}'.format(
                  image, e))


@zeit.web.register_filter
def pluralize(num, *forms):
    try:
        num = '{:,d}'.format(int(num)).replace(',', '.')
    except ValueError:
        num = 0
    return forms[min(len(forms) - 1, num):][0].format(num)


@zeit.web.register_filter
def unitize(num, select_token=None):
    if num <= 999:
        tokens = str(num), ''
    elif num <= 9999:
        tokens = ','.join(list(str(num))[:2]), 'Tsd.'
    elif num <= 999999:
        tokens = str(num / 1000), 'Tsd.'
    else:
        tokens = str(num / 1000000), 'Mio.'
    if select_token is None:
        return ' '.join(tokens)
    else:
        return tokens[select_token]


@zeit.web.register_filter
def with_mods(b_or_e, *mods):
    """Decorate a BEM-style block or element with an a set of modifiers."""
    return ' '.join([b_or_e] + ['{}--{}'.format(b_or_e, m) for m in
                                set(mods) if isinstance(m, basestring)])


@zeit.web.register_filter
def get_attr(*args):
    return getattr(*args)


@zeit.web.register_filter
def topic_links(context):
    return zeit.web.core.interfaces.ITopicLink(context, None)


@zeit.web.register_filter
def pop_from_dotted_name(string, index=-1):
    try:
        return string.split('.').pop(index)
    except AttributeError:
        return


@zeit.web.register_ctxfilter
def macro(context, macro_name, *args, **kwargs):
    """Call a macro extracted from the context by its name."""
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
    # TRASHME: This is solved by legacy variant image configuration
    layout = zeit.content.cp.layout.TEASERBLOCK_LAYOUTS
    layout_image = {block.id: [block.image_pattern] for block in
                    list(layout(None)) if block.image_pattern}
    try:
        layout_image['zon-small'].extend(layout_image['leader'])
        layout_image['zon-parquet-small'].extend(layout_image['leader'])
        layout_image['zon-parquet-large'].extend(layout_image['leader'])
        layout_image['zon-fullwidth'].extend(layout_image['leader-fullwidth'])
        layout_image['zon-classic'].extend(layout_image['leader-fullwidth'])
        layout_image['zon-large'].extend(layout_image['leader'])
        layout_image['zon-series'].extend(layout_image['leader'])
        layout_image['zon-column'].extend(layout_image['leader'])
        layout_image['zon-square'].extend(layout_image['leader'])
        layout_image['zon-blog'].extend(layout_image['leader'])
        layout_image['topic'].extend(layout_image['leader-fullwidth'])
    except KeyError, e:
        log.warn("Layouts for '%s' could not be extended: %s not found",
                 teaser_layout, e)

    return layout_image.get(teaser_layout, [orig_image_pattern])


def _existing_image(image_group, patterns, ext):
    # TRASHME: Only needed by deprecated get_teaser_image function
    filenames = image_group.keys()
    for pattern in patterns:
        for name in filenames:
            if name.endswith('{}.{}'.format(pattern, ext)):
                return image_group[name], pattern
    return None, None


@zeit.web.register_global
def get_column_image(content):
    # XXX: Could be transformed to a more generally useful get_author
    try:
        author = content.authorships[0].target
    except (AttributeError, IndexError, TypeError):
        return
    # XXX This should use a different variant, but author images currently do
    # not have a consistent ratio and framing of the portrayed person. So we
    # need to crop the lower part of the image using CSS, ignoring the ratio.
    return get_image(content=author, variant_id='original', fallback=False)


@zeit.web.register_global
def get_teaser_image(teaser_block, teaser, unique_id=None):
    # TRASHME: Deprecated for zci images in favour of get_image
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

    # If imagegroup has no images, return default image
    if len(asset) == 0:
        return get_teaser_image(teaser_block, teaser, unique_id=default_id)

    try:
        image_patterns = get_image_pattern(
            get_layout(teaser_block), teaser_block.layout.image_pattern)
    except AttributeError:
        return

    # We assume all images in a group have the same mimetype.
    sample_image = u'{}{}'.format(asset.uniqueId, asset.keys()[0])
    ext = {'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png'}.get(
        mimetypes.guess_type(sample_image)[0], 'jpg')

    image, image_pattern = _existing_image(asset, image_patterns, ext)
    if image is None:
        image_pattern = teaser_block.layout.image_pattern
        image, _ = _existing_image(asset, [image_pattern], ext)
    if zeit.web.core.image.is_image_expired(image):
        return None

    if image is None:
        log.debug('Cannot retrieve teaser image {} for {}'.format(
            image_pattern, unique_id or asset.uniqueId))
        # Don't fallback when a unique_id is given explicitly in order to
        # prevent infinite recursion.
        if not unique_id:
            return get_teaser_image(teaser_block, teaser, unique_id=default_id)

    teaser_image = zope.component.getMultiAdapter(
        (asset, image), zeit.web.core.interfaces.ITeaserImage)
    teaser_image.image_pattern = image_pattern
    return teaser_image


@zeit.web.register_filter
def get_image_group(asset):
    # TRASHME: Should be solved by using get_image on video modules
    try:
        return zeit.content.image.interfaces.IImageGroup(asset)
    except TypeError:
        return


@zeit.web.register_filter
def get_module(module, name=None):
    if zeit.web.core.interfaces.IBlock.providedBy(module):
        return module
    elif zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(module):
        return module
    elif zeit.content.cp.interfaces.ICPExtraBlock.providedBy(module):
        name = 'cpextra'
    elif zeit.edit.interfaces.IBlock.providedBy(module):
        name = 'type'
    else:
        return module

    return zeit.web.core.utils.get_named_adapter(
        module, zeit.web.core.interfaces.IBlock, name)


@zeit.web.register_filter
def attr_safe(string):
    """Return an attribute safe version of string"""
    if isinstance(string, basestring):
        return re.sub('[^a-zA-Z]', '', string).lower()
    return string


@zeit.web.register_filter
def format_webtrekk(string):
    """Returns a string that is webtrekk-safe.
    This code does the same as sanitizeString in clicktracking.js
    """
    if not isinstance(string, basestring):
        return string
    string = string.lower().replace(
        u'ä', 'ae').replace(
        u'ö', 'oe').replace(
        u'ü', 'ue').replace(
        u'á', 'a').replace(
        u'à', 'a').replace(
        u'é', 'e').replace(
        u'è', 'e').replace(
        u'ß', 'ss')
    string = re.sub(u'[^-a-zA-Z0-9]', '_', string)
    string = re.sub(u'_+', '_', string)
    string = re.sub(u'^_|_$', '', string)
    return string


@zeit.web.register_filter
def format_iqd(string):
    """Returns a string that is iqd-safe.
    Only allows latin characters, numbers and underscore.
    """
    if not isinstance(string, basestring):
        return string
    string = string.lower().replace(
        u'ä', 'ae').replace(
        u'ö', 'oe').replace(
        u'ü', 'ue').replace(
        u'á', 'a').replace(
        u'à', 'a').replace(
        u'é', 'e').replace(
        u'è', 'e').replace(
        u'ß', 'ss')
    string = re.sub(u'[^a-zA-Z0-9]', '_', string)
    string = re.sub(u'_+', '_', string)
    string = re.sub(u'^_|_$', '', string)
    return string


@zeit.web.register_global
def settings(key, default=None):
    """Returns the configuration value for a provided key"""
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get(key, default)


@zeit.web.register_global
def toggles(*keys):
    """Returns whether all provided feature toggles are enabled"""
    toggles = zeit.web.core.application.FEATURE_TOGGLES
    return all(toggles.find(key) for key in keys)


@zeit.web.register_global
def interrupt(reason=None):
    if toggles('instantarticle_interrupts'):
        raise zeit.web.core.jinja.Interrupt(reason)
    else:
        return u''


@zeit.web.register_global
def to_list(iterable):
    return types.ListType(iterable)


@zeit.web.register_global
def to_tuple(iterable):
    return types.TupleType(iterable)


@zeit.web.register_global
def to_dict(mapping):
    return types.DictType(mapping)


@zeit.web.register_global
def debug_breaking_news(request):
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
    # XXX Should we rather get the request automatically (as a ctxfilter)?
    # Usage then would be `{{ url | append_get_params(foo='bar') }}`.
    base_url = kw.pop('url', request.path_url)

    # Append GET parameters that are not reset
    # by setting the param value to None explicitly.
    def encode(value):
        return unicode(value).encode('utf-8')

    params = [(encode(k), encode(v)) for k, v in itertools.chain(
              (i for i in request.GET.iteritems() if i[0] not in kw),
              (i for i in kw.iteritems() if i[1] is not None))]

    if params == []:
        return base_url
    return u'{}?{}'.format(base_url, urllib.urlencode(params))


@zeit.web.register_filter
def remove_get_params(url, *args):
    # ToDo: This should be used in templates,
    # if append_get_params gets refactored.
    # It'd be more useful to use these functions on URL and not request level
    # This way we could say sth. like
    # `request | make_url() |
    #  append_get_params(foo='ba', ba='batz') | remove_get_params('foobar')`
    # and vice versa.

    scheme, netloc, path, query, frag = urlparse.urlsplit(url)
    query_p = urlparse.parse_qs(query)
    for arg in args:
        query_p.pop(arg, None)
    if len(query_p) == 0:
        return '{}://{}{}'.format(
            scheme, netloc, path)
    else:
        return '{}://{}{}?{}'.format(
            scheme, netloc, path, urllib.urlencode(query_p, doseq=True))


@zeit.web.register_filter
def join_if_exists(iterable, string=''):
    """Join list items through string, if item is not None"""
    return string.join([item for item in iterable if item])


@zeit.web.register_global
def provides(obj, iface):
    try:
        iface = pyramid.path.DottedNameResolver().resolve(iface)
    except ValueError:
        return False
    return iface.providedBy(obj)


@zeit.web.register_global
def get_random_number(length):
    return random.randint(0, 10 ** length)


@zeit.web.register_global
def adapt(obj, iface, name=u'', multi=False):
    iface = pyramid.path.DottedNameResolver().resolve(iface)
    if multi:
        return zope.component.queryMultiAdapter(obj, iface, name)
    else:
        return zope.component.queryAdapter(obj, iface, name)
