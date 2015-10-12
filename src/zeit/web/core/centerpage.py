import logging

import grokcore.component
import zope.component

import zeit.cms.interfaces
import zeit.content.cp.area
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.block
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
    except TypeError:
        return

    if asset.video is not None:
        asset.video.highest_rendition = get_video_source(asset.video)

    if asset.video_2 is not None and asset.video is not None:
        asset.video_2.highest_rendition = get_video_source(asset.video_2)
        return [asset.video, asset.video_2]

    return asset.video


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


class IRendered(zope.interface.Interface):
    """Calculates values() only once.
    """


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


class TeaserSequence(object):

    def __init__(self, context):
        self.context = context
        self.sequence = []
        self.refs = []

    def __contains__(self, item):
        return item in self.sequence

    def __iter__(self):
        return iter(self.sequence)

    def __len__(self):
        return len(self.sequence)

    def __setitem__(self, key, value):
        index = self.sequence.index(key)
        self.refs[index][key] = value

    def __getitem__(self, key):
        return self.sequence[key]

    def __delitem__(self, key):
        del self.sequence[key]

    def __repr__(self):
        return object.__repr__(self)

    def _resolve_child(self, item):
        try:
            sub_seq = zeit.web.core.interfaces.ITeaserSequence(item)
            self.sequence += sub_seq.sequence
            self.refs += sub_seq.refs
            return
        except TypeError:
            pass
        try:
            self.sequence.append(zeit.web.core.centerpage.Teaser(
                self.context, item))
            self.refs.append(self.context)
        except TypeError:
            pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(list)
class TeaserList(TeaserSequence):

    def __init__(self, context):
        super(TeaserList, self).__init__(context)
        for item in iter(context):
            self._resolve_child(item)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
class TeaserBlock(TeaserList):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(dict)
class TeaserDict(TeaserSequence):

    def __init__(self, context):
        super(TeaserDict, self).__init__(context)
        for item in context.itervalues():
            self._resolve_child(item)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
class Area(TeaserDict):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaser)
@grokcore.component.adapter(TeaserSequence, zeit.cms.interfaces.ICMSContent)
class Teaser(object):

    def __init__(self, block, context):
        self.video = None
        self.gallery = None
        self.image = zeit.web.core.template.get_teaser_image(block, context)
        self.context = context


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
class TopicLink(zeit.web.core.utils.nslist):
    """Filter and restructure all topiclinks and labels
    :rtype: generator
    """

    def __init__(self, context):
        self.context = context
        self.title = context.topiclink_title or 'Schwerpunkte'
        for i in xrange(1, 4):
            label = getattr(self.context, 'topiclink_label_%s' % i, None)
            link = getattr(self.context, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                self.append((label, link))


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.web.core.interfaces.INextread)
class Nextread(TeaserBlock):
    pass
