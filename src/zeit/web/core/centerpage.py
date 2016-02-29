import logging

import grokcore.component
import zope.component
import zope.interface
import pyramid.threadlocal

import zeit.cms.interfaces
import zeit.content.author.interfaces
import zeit.content.cp.area
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


@zeit.web.register_filter
def get_area(area):
    return zeit.web.core.utils.get_named_adapter(
        area, zeit.content.cp.interfaces.IRenderedArea, 'kind')


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
    context._v_values = context.values()
    context.values = cached_values.__get__(context)
    return context


class TeaserMapping(zeit.web.core.utils.frozendict):

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
        super(TeaserMapping, self).__init__(
            x for k, v in self._map.iteritems() for x in zip(v, [k] * len(v)))

TEASER_MAPPING = TeaserMapping()


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
