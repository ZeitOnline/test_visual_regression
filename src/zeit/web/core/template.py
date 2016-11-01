# coding: utf8
import collections
import datetime
import logging
import pkg_resources
import random
import re
import time
import types
import urllib
import urlparse

import babel.dates
import lxml.etree
import pyramid.threadlocal
import zope.component

import zeit.campus.interfaces
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces
import zeit.magazin.interfaces

import zeit.web
import zeit.web.core.application
import zeit.web.core.centerpage
import zeit.web.core.image
import zeit.web.core.interfaces
import zeit.web.core.utils

log = logging.getLogger(__name__)

SHORT_TERM_CACHE = zeit.web.core.cache.get_region('short_term')


@zeit.web.register_global
def get_image(context, variant_id=None, fallback=True, fill_color=True,
              name=u''):
    """Universal image retrieval function to be used in templates.

    :param context:     Context of which to extract the image from
    :param fallback:    Set whether missing image should render a fallback:
                            True    Render the default fallback image
                            False   Do not render a fallback at all
                            'foo'   Render the fallback image configured under
                                    the zeit.web settings key 'foo'
    :param variant_id:  Override for automatic variant_id determination
    :param fill_color:  Fill images with transparent background with color:
                            True    Determine automatically
                            False   Keep background transparent
                            'red'   Red fill color
                            '00F'   Blue fill color
    :param name:        Image extraction for a specific context type can be
                        overloaded with multiple extraction methods.
                        These can be applied via the name parameter:
                            content Select the first element from a container
                                    object and retrieve the image from there
                                    (e.g. first entry of a gallery or first
                                     teaser in a block)
                            sharing Select an image suitable for sharing the
                                    content item on social media platforms
                            author  Select the (first) author's portrait

    :rtype:             zeit.web.core.interfaces.IImage
    """

    try:
        if name == u'':
            # For unnamed adapters we can rely on zope interface mechanics
            # to determine whether our context already provides IImage.
            image = zeit.web.core.interfaces.IImage(context)
        else:
            # For named adapters we have no chance of verifying the name
            # requirement without a component lookup.
            image = zope.component.getAdapter(
                context, zeit.web.core.interfaces.IImage, name)
    except (zope.component.ComponentLookupError, TypeError):
        image = None

    if not bool(image) or expired(image):
        # To clarify, that we do not only want to test against None but also
        # for invalid images, we cast to boolean.
        if fallback is False:
            return None
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if fallback is True:
            default_id = conf.get('default_teaser_images')
        else:
            default_id = conf.get(fallback, '')
        context = zeit.cms.interfaces.ICMSContent(default_id, None)
        if image is None:
            image = zeit.web.core.interfaces.IImage(context, None)
        else:
            # If we managed to create a (broken) image earlier, we can reuse
            # it to maintain its settings (ie. variant).
            image.group = context

    if not bool(image):
        return None

    if not fill_color:
        image.fill_color = None
    elif fill_color is not True:
        image.fill_color = fill_color

    if variant_id is not None:
        image.variant_id = variant_id

    return image


@zeit.web.register_test
def zmo_content(content):
    # XXX Stopgap until longforms are not IZMOContent anymore (ZON-2411).
    return not getattr(content, 'uniqueId', '').replace(
        zeit.cms.interfaces.ID_NAMESPACE, '', 1).startswith('feature') and (
            zeit.magazin.interfaces.IZMOContent.providedBy(content))


@zeit.web.register_test
def zplus_content(content):
    if not zeit.web.core.application.FEATURE_TOGGLES.find('reader_revenue'):
        return False

    # Links are defined as free content
    if zeit.content.link.interfaces.ILink.providedBy(content):
        return False

    access = getattr(content, 'access', None)
    if access is None:
        return False
    return (access == 'abo')


@zeit.web.register_test
def zett_content(content):
    return zeit.content.link.interfaces.ILink.providedBy(
        content) and content.url.startswith('http://ze.tt')


@zeit.web.register_test
def zco_content(content):
    return zeit.campus.interfaces.IZCOContent.providedBy(content)


@zeit.web.register_test
def liveblog(context):
    return zeit.content.article.interfaces.IArticle.providedBy(
        context) and context.template == 'zon-liveblog'


@zeit.web.register_test
def column(context):
    return context.serie and context.serie.column


@zeit.web.register_test
def leserartikel(context):
    return getattr(context, 'genre', None) and context.genre == 'leserartikel'


@zeit.web.register_test
def hidden_slide(context):
    if zeit.content.gallery.interfaces.IGalleryEntry.providedBy(context):
        return context.layout == 'hidden'


@zeit.web.register_test
def framebuilder(view):
    return isinstance(view, zeit.web.core.view.FrameBuilder)


@zeit.web.register_test
def paragraph(block):
    return block_type(block) == 'paragraph'


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
    elif getattr(obj, 'block_type', None):
        return obj.block_type
    else:
        return type(obj).__name__.lower()


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
        return create_url(
            context, u'{}/{}'.format(obj.uniqueId, obj.seo_slug), request)
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
    elif type == 'switch_from_hours_to_date':
        delta = datetime.datetime.now(date.tzinfo) - date
        if delta.days >= int(1):
            pattern = 'dd. MM. yyyy'
        elif delta.days < int(1):
            pattern = "'Heute,' HH:mm"
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
def neighborhood(iterable, default=None):
    return zeit.web.core.utils.neighborhood(iterable, default)


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
@zeit.web.cache_on_request
def get_layout(block):
    try:
        layout = block.layout.id
    except (AttributeError, TypeError):
        return 'hide'
    if zeit.content.cp.interfaces.ITeaserBlock.providedBy(
            block) and not len(block):
        return 'hide'
    layout = zeit.web.core.centerpage.LEGACY_TEASER_MAPPING.get(layout, layout)
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
def comment_tracking_row(context):
    try:
        return context.split('.', 1)[0]
    except:
        return ''


@zeit.web.register_filter
def comment_tracking_col(context):
    try:
        return context.split('.', 1)[1]
    except:
        return 0


@zeit.web.register_filter
def pluralize(num, *forms):
    try:
        value = int(num)
        display = '{:,d}'.format(value).replace(',', '.')
    except ValueError:
        display = value = 0
    return forms[min(len(forms) - 1, value):][0].format(display)


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
    url = kw.pop('url', request.url)
    return zeit.web.core.utils.add_get_params(url, **kw)


@zeit.web.register_filter
def remove_get_params(url, *args):
    return zeit.web.core.utils.remove_get_params(url, *args)


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


# I'd rather use the spelling `isinstance`, but that would clobber it for this
# module, so that's a no-go.
@zeit.web.register_global
def is_instance(obj, cls):
    try:
        cls = pyramid.path.DottedNameResolver().resolve(cls)
    except ValueError:
        return False
    return isinstance(obj, cls)


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


@SHORT_TERM_CACHE.cache_on_arguments()
def get_svg_from_file_cached(name, class_name, package, cleanup, a11y):
    try:
        subpath = '.'.join(package.split('.')[1:3])
    except (AttributeError, TypeError):
        log.debug('Icon: {} has false package'.format(name))
        return ''
    url = pkg_resources.resource_filename(
        'zeit.web.static', 'css/svg/{}/{}.svg'.format(subpath, name))
    try:
        xml = lxml.etree.parse(url)
    except (IOError, lxml.etree.XMLSyntaxError):
        return ''
    try:
        title = xml.find('{http://www.w3.org/2000/svg}title').text
    except AttributeError:
        title = 'Icon'
    svg = xml.getroot()
    svg.set('class', 'svg-symbol {}'.format(class_name))
    svg.set('preserveAspectRatio', 'xMinYMin meet')
    if cleanup:
        lxml.etree.strip_attributes(
            xml, 'fill', 'fill-opacity', 'stroke', 'stroke-width')
    if a11y:
        svg.set('role', 'img')
        svg.set('aria-label', title)
    else:
        svg.set('aria-hidden', 'true')
    return lxml.etree.tostring(xml)


@zeit.web.register_global
def get_svg_from_file(name, class_name, package, cleanup, a11y):
    return get_svg_from_file_cached(name, class_name, package, cleanup, a11y)


@zeit.web.register_test
def expired(content):
    info = zeit.web.core.interfaces.IExpiration(content, None)
    if info is None:
        return False
    return info.is_expired
