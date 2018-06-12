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
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.edit.interfaces

import zeit.solr.connection

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.utils


log = logging.getLogger(__name__)


class InMemoryMixin(object):
    """Overrides relevant methods of zeit.edit.container.Base to use a dict
    instead of an XML node as storage. To instantiate, pass the respective
    parent object (an IBody or IRegion).

    InMemory Region and Area are meant to contain items that are already
    zeit.web-wrapped (that is, equivalents to what comes out of
    `IRendered(get_area())` or `get_module()`, respectively).
    This can be helpful either for performance reasons (i.e. if using the
    normal XML-backed classes from zeit.content.cp is too much overhead), or in
    cases where there is no vivi-equivalent for the modules in question (e.g.
    the comments area in zeit.web.site.view_author which displays a comment
    dict as if it were an ICMSContent inside a teaser module).
    """

    _factory = NotImplemented

    __name__ = None

    def __init__(self, context):
        super(InMemoryMixin, self).__init__(context, self._factory.get_xml())
        self._data = collections.OrderedDict()
        self.__name__ = str(uuid.uuid4())

    def __getitem__(self, key):
        return self._data[key]

    def _get_keys(self, xml_node):
        return self._data.keys()

    def _add(self, item):
        key = self._get_unique_name(item)
        item.__name__ = key
        self._data[key] = item
        return key

    def _delete(self, key):
        del self._data[key]


class Region(InMemoryMixin, zeit.content.cp.area.Region):

    _factory = zeit.content.cp.area.RegionFactory(None)


class Area(InMemoryMixin, zeit.content.cp.area.Area):

    _factory = zeit.content.cp.area.AreaFactory(None)


@zeit.web.register_global
def get_video(context):
    try:
        asset = zeit.content.video.interfaces.IVideoAsset(context)
        primary = asset.video
        secondary = asset.video_2
    except (TypeError, AttributeError):
        return

    if secondary is not None and primary is not None:
        return [primary, secondary]
    else:
        return primary


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
def images_from_teaserblock(context):
    try:
        content = list(context)[0]
    except IndexError:
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt', context, zeit.web.core.interfaces.IImage)
    return zeit.content.image.interfaces.IImages(content, None)


@zeit.web.register_filter
def get_area(area):
    return zeit.web.core.utils.get_named_adapter(
        area, zeit.content.cp.interfaces.IRenderedArea, 'kind')


def get_module(module):
    """Wraps a zeit.edit.interfaces.IBlock into a
    zeit.web.core.interfaces.IBlock. If no specific adapter is available, a
    generic `Module` object (see below) is returned, with a `layout` whose `id`
    is the IBlock.type.
    """
    if zeit.web.core.interfaces.IBlock.providedBy(module):
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
                              for x in super(RenderedRegion, self).values()
                              if x.visible]
        return self._v_values


@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
@grokcore.component.implementer(IRendered)
def cache_values_area(context):
    def cached_values(self):
        return self._v_values
    context._v_values = [get_module(x)
                         for x in context.values()
                         if x.visible]
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
            link = zeit.web.core.utils.maybe_convert_http_to_https(
                getattr(self.context, 'topiclink_url_%s' % i, None))
            if label is not None and link is not None:
                self.append((label, link))


@zeit.web.register_module(u'')
class Module(object):
    """Base class for RAM-style modules.

    See `zeit.web.core.decorator.register_module` for doc and example.
    """

    __parent__ = NotImplemented

    def __init__(self, context):
        self.context = context
        if zeit.content.cp.interfaces.ICPExtraBlock.providedBy(context):
            self.layout = context.cpextra
        elif zeit.edit.interfaces.IBlock.providedBy(context):
            self.layout = context.type

    def __getattr__(self, name):
        return getattr(self.context, name)

    def __hash__(self):
        return self.context.xml.get(
            '{http://namespaces.zeit.de/CMS/cp}__name__',
            super(Module, self)).__hash__()

    def __repr__(self):
        return object.__repr__(self)

    @zeit.web.reify
    def __name__(self):
        return self.context.__name__

    @property
    def layout(self):
        return getattr(self, '_layout', None)

    @layout.setter
    def layout(self, value):
        self._layout = zeit.content.cp.layout.get_layout(value) or (
            zeit.content.cp.layout.BlockLayout(
                value, value, areas=[], image_pattern=value))

    @property
    def request(self):
        # XXX Yes, yes, it's bad practice. But milking the request object
        #     during traversal is ever so slightly more horrible. (ND)
        return pyramid.threadlocal.get_current_request()

    @zeit.web.reify
    def visible(self):
        return getattr(self.context, 'visible', True)


@zope.interface.implementer(zeit.web.core.interfaces.IBlock)
class TeaserModule(Module, zeit.web.core.utils.nslist):

    visible = True

    def __init__(self, context, **kw):
        Module.__init__(self, context)
        zeit.web.core.utils.nslist.__init__(self, [v for v in context if v])
        self._layout = kw.pop('layout', 'default')
        self.type = kw.pop('type', 'teaser')
        self.__parent__ = kw.pop('parent', None)

    def __hash__(self):
        return hash((self.layout.id, id(self)))

    def __repr__(self):
        return object.__repr__(self)

    @zeit.web.reify
    def layout(self):
        if self._layout:
            layout = LEGACY_TEASER_MAPPING.get(self._layout, self._layout)
            layout = zeit.content.cp.layout.get_layout(layout)
            if layout:
                return layout
            else:
                id = self._layout
                return zeit.content.cp.layout.BlockLayout(
                    id, id, areas=[], image_pattern=id)
        return super(TeaserModule, self).layout


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(TeaserModule)
def images_from_teasermodule(context):
    try:
        content = list(context)[0]
    except IndexError:
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt', context, zeit.content.image.interfaces.IImages)
    return zeit.content.image.interfaces.IImages(content, None)


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


original_search = zeit.solr.connection.SolrConnection.search
zeit.solr.connection.SolrConnection.search = search_with_timing_metrics


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


@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@grokcore.component.implementer(zeit.web.core.interfaces.ISeries)
class Series(object):
    def __init__(self, context):
        self.context = context

    @zeit.web.reify
    def kind(self):
        try:
            return self.context.serie.kind
        except AttributeError:
            return True

    @zeit.web.reify
    def title(self):
        return self.context.serie.title

    @zeit.web.reify
    def podcastseries_feed(self):
        podcastfeed = self.context.serie.url
        return podcastfeed.replace("-", "")
