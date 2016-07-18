import collections
import logging
import uuid

import grokcore.component
import zope.interface
import pyramid.threadlocal

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.blocks.automatic
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.edit.interfaces

import zeit.find.search

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.utils


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.content.cp.interfaces.IArea)
class Area(collections.OrderedDict):

    factory = zeit.content.cp.area.AreaFactory(None)

    def __init__(self, arg, **kw):
        super(Area, self).__init__(
            [('id-{}'.format(uuid.uuid1()), get_module(v)) for v in arg if v])
        self.kind = kw.pop('kind', 'solo')
        self.xml = kw.pop('xml', self.factory.get_xml())
        self.automatic = kw.pop('automatic', False)
        self.__parent__ = kw.pop('parent', None)

        for key in kw:
            try:
                assert not hasattr(self, key)
                setattr(self, key, kw[key])
            except:
                continue

    def append(self, value):
        self['id-{}'.format(uuid.uuid1())] = value

    def __hash__(self):
        if self.kind:
            return hash((self.kind, id(self)))
        else:
            raise NotImplementedError()

    def __repr__(self):
        return object.__repr__(self)

    # XXX This is really crude, but since these Legacy-classes throw away
    # their vivi-side objects, we can't get to the interfaces anymore,
    # so a full re-implementation is just plain impossible.
    # So we hard-code the only use-case that this should ever be called for,
    # which is ITeaseredContent.
    def select_modules(self, *interfaces):
        for module in zeit.content.cp.interfaces.IRenderedArea(self).values():
            if getattr(module, 'type', None) == 'teaser':
                yield module


@zope.interface.implementer(zeit.content.cp.interfaces.IRegion)
class Region(Area):

    factory = zeit.content.cp.area.RegionFactory(None)


@zeit.web.register_filter
def auto_select_asset(teaser):
    for getter in (get_video_asset, get_gallery_asset, get_image_asset):
        asset = getter(teaser)
        if asset:
            return asset
    log.debug('No assets for %s' % teaser.uniqueId)


@zeit.web.register_filter
def get_video_asset(teaser):

    def get_video_source(self):
        try:
            highest_rendition = self.renditions[0]
            for rendition in self.renditions:
                if highest_rendition.frame_width < rendition.frame_width:
                    highest_rendition = rendition
            return highest_rendition.url
        except (AttributeError, IndexError, TypeError):
            return self.flv_url

    try:
        asset = zeit.content.video.interfaces.IVideoAsset(teaser)
        primary = asset.video
        secondary = asset.video_2
    except TypeError:
        return

    if primary is not None:
        primary.highest_rendition = get_video_source(primary)

    if secondary is not None and primary is not None:
        secondary.highest_rendition = get_video_source(secondary)
        return [primary, secondary]

    return primary


@zeit.web.register_filter
def get_gallery_asset(teaser):
    try:
        return zeit.content.gallery.interfaces.IGalleryReference(
            teaser).gallery
    except (TypeError, AttributeError):
        return


@zeit.web.register_filter
def get_image_asset(teaser):
    try:
        return zeit.content.image.interfaces.IImages(teaser).image
    except (TypeError, AttributeError):
        return


def get_area(area):
    return zeit.web.core.utils.get_named_adapter(
        area, zeit.content.cp.interfaces.IRenderedArea, 'kind')


def get_module(module):
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


class IRendered(zope.interface.Interface):
    """Calculates values() only once."""


@grokcore.component.adapter(zeit.content.cp.interfaces.IRegion)
@grokcore.component.implementer(IRendered)
class RenderedRegion(zeit.content.cp.area.Region):

    def __init__(self, context):
        super(RenderedRegion, self).__init__(context.__parent__, context.xml)

    def values(self):
        if not hasattr(self, '_v_values'):
            self._v_values = [IRendered(get_area(x))
                              for x in super(RenderedRegion, self).values()]
        return self._v_values


@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
@grokcore.component.implementer(IRendered)
def cache_values_area(context):
    def cached_values(self):
        return self._v_values
    context._v_values = [get_module(x) for x in context.values()]
    context.values = cached_values.__get__(context)
    return context


class LegacyTeaserMapping(zeit.web.core.utils.frozendict):

    _map = {'zon-large': ['leader', 'leader-two-columns', 'leader-panorama',
                          'parquet-large', 'zon-parquet-large'],
            'zon-small': ['text-teaser', 'buttons', 'large', 'short', 'date',
                          'parquet-regular', 'zon-parquet-small'],
            'zon-fullwidth': ['leader-fullwidth'],
            'zon-inhouse': ['parquet-verlag'],
            'hide': ['archive-print-volume', 'archive-print-year',
                     'two-side-by-side', 'ressort', 'leader-upright',
                     'buttons-fullwidth', 'parquet-printteaser']}

    def __init__(self, *args, **kw):
        # Flattens and reverses _map, so we can easily lookup a layout.
        super(LegacyTeaserMapping, self).__init__(
            x for k, v in self._map.iteritems() for x in zip(v, [k] * len(v)))

LEGACY_TEASER_MAPPING = LegacyTeaserMapping()


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
class TopicLink(zeit.web.core.utils.nslist):
    """Filter and restructure all topiclinks and labels"""

    def __init__(self, context):
        self.context = context
        self.title = getattr(context, 'topiclink_title', '') or 'Schwerpunkte'
        for i in xrange(1, 4):
            label = getattr(self.context, 'topiclink_label_%s' % i, None)
            link = getattr(self.context, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                self.append((label, link))


@zeit.web.register_module(u'')
class Module(object):
    """Base class for RAM-style modules to be used in cp2015 centerpages.

    See `zeit.web.core.decorator.register_module` for doc and example.
    """

    __parent__ = NotImplemented

    def __init__(self, context):
        self.context = context
        if zeit.content.cp.interfaces.ICPExtraBlock.providedBy(context):
            self.layout = context.cpextra
        elif zeit.edit.interfaces.IBlock.providedBy(context):
            self.layout = context.type

    def __hash__(self):
        return self.context.xml.attrib.get(
            '{http://namespaces.zeit.de/CMS/cp}__name__',
            super(Module, self)).__hash__()

    def __repr__(self):
        return object.__repr__(self)

    @property
    def layout(self):
        return getattr(self, '_layout', None)

    @layout.setter
    def layout(self, value):
        self._layout = zeit.content.cp.layout.BlockLayout(
            value, value, areas=[], image_pattern=value)

    @property
    def request(self):
        # XXX Yes, yes, it's bad practice. But milking the request object
        #     during traversal is ever so slightly more horrible. (ND)
        return pyramid.threadlocal.get_current_request()


@zope.interface.implementer(zeit.web.core.interfaces.IBlock)
class TeaserModule(Module, zeit.web.core.utils.nslist):

    def __init__(self, arg, **kw):
        zeit.web.core.utils.nslist.__init__(self, [v for v in arg if v])
        self.layout = kw.pop('layout', 'default')
        self.type = kw.pop('type', 'teaser')
        self.__parent = kw.pop('parent', None)

    def __hash__(self):
        return hash((self.layout.id, id(self)))

    def __repr__(self):
        return object.__repr__(self)


@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@grokcore.component.implementer(zeit.web.core.interfaces.IDetailedContentType)
def cp_detailed_content_type(context):
    subtyp = context.type
    if zeit.web.core.view.is_advertorial(context, None):
        subtyp = 'advertorial'
    result = 'centerpage.{}'.format(subtyp)
    seo = zeit.seo.interfaces.ISEO(context)
    if seo.keyword_entity_type:
        result += '.' + seo.keyword_entity_type.lower()
    return result


# Add timing metrics for solr to zeit.content.cp.interfaces.IRenderedArea
def search_with_timing_metrics(*args, **kw):
    with zeit.web.core.metrics.timer(
            'zeit.web.site.area.default.solr.reponse_time'):
        return original_search(*args, **kw)
original_search = zeit.find.search.search
zeit.find.search.search = search_with_timing_metrics


# We can't do anything with non-existent content (as opposed to vivi where
# showing placeholders might give some benefit), so we don't bother with
# FakeEntry, as zeit.cms.syndication.feed.ContentList does.
def iter_without_fakeentry(self):
    for unique_id in self.keys():
        try:
            yield zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            continue
zeit.content.cp.blocks.teaser.TeaserBlock.__iter__ = iter_without_fakeentry


# Simply pass through whatever teaser layout is set in XML, ignoring the
# availability rules.
def layout_or_fake(instance):
    result = instance.original_layout(instance)
    # We still need to return None for __init__, so it sets the default layout.
    if result or (instance.xml.get('module') in ['teaser', 'auto-teaser']):
        return result
    return zeit.content.cp.layout.BlockLayout(
        id, id, areas=[], image_pattern=id)
zeit.content.cp.blocks.teaser.TeaserBlock.original_layout = (
    zeit.content.cp.blocks.teaser.TeaserBlock.layout.__get__)
zeit.content.cp.blocks.teaser.TeaserBlock.layout = property(
    layout_or_fake, zeit.content.cp.blocks.teaser.TeaserBlock.layout.__set__)
zeit.content.cp.blocks.automatic.AutomaticTeaserBlock.original_layout = (
    zeit.content.cp.blocks.automatic.AutomaticTeaserBlock.layout.__get__)
zeit.content.cp.blocks.automatic.AutomaticTeaserBlock.layout = property(
    layout_or_fake,
    zeit.content.cp.blocks.automatic.AutomaticTeaserBlock.layout.__set__)

zeit.content.cp.layout.BlockLayout.is_allowed = lambda *args, **kw: True
