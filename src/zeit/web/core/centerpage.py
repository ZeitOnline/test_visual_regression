import grokcore.component

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.block
import zeit.web.core.interfaces

import logging

log = logging.getLogger(__name__)


@zeit.web.register_filter
def get_all_assets(teaser):
    try:
        assets = (get_video_asset(teaser),
                  get_gallery_asset(teaser),
                  get_image_asset(teaser))
        return tuple(a for a in assets if a)
    except TypeError:
        log.debug('No assets for %s' % teaser.uniqueId)
        return ()


@zeit.web.register_filter
def auto_select_asset(teaser):
    assets = get_all_assets(teaser)
    if len(assets):
        return assets[0]


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

    asset = zeit.content.video.interfaces.IVideoAsset(teaser)

    if asset.video is not None:
        asset.video.highest_rendition = get_video_source(asset.video)

    if asset.video_2 is not None and asset.video is not None:
        asset.video_2.highest_rendition = get_video_source(asset.video_2)
        return [asset.video, asset.video_2]

    return asset.video


def get_gallery_asset(teaser):
    asset = zeit.content.gallery.interfaces.IGalleryReference(teaser)
    return asset.gallery


@zeit.web.register_filter
def get_image_asset(teaser):
    asset = zeit.content.image.interfaces.IImages(teaser)
    return asset.image


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
@grokcore.component.adapter(zeit.content.cp.interfaces.IAutoPilotTeaserBlock)
class AutoPilotTeaserBlock(TeaserBlock):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(dict)
class TeaserDict(TeaserSequence):

    def __init__(self, context):
        super(TeaserDict, self).__init__(context)
        for item in context.itervalues():
            self._resolve_child(item)


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBar)
class TeaserBar(TeaserDict):

    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaser)
@grokcore.component.adapter(TeaserSequence, zeit.cms.interfaces.ICMSContent)
class Teaser(object):

    def __init__(self, block, context):
        self.video = None
        self.gallery = None
        self.image = zeit.web.core.template.get_teaser_image(block, context)
        self.context = context


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
class Image(zeit.web.core.block.BaseImage):

    def __init__(self, image):
        meta = zeit.content.image.interfaces.IImageMetadata(image)
        self.align = None
        self.alt = meta.alt
        self.attr_alt = meta.alt or meta.caption
        self.attr_title = meta.title or meta.caption
        self.caption = meta.caption
        self.copyright = meta.copyrights
        self.image = image
        self.image_group = None
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId
        self.title = meta.title


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserImage)
@grokcore.component.adapter(zeit.content.image.interfaces.IImageGroup,
                            zeit.content.image.interfaces.IImage)
class TeaserImage(zeit.web.core.block.BaseImage):

    def __init__(self, image_group, image):
        meta = zeit.content.image.interfaces.IImageMetadata(image_group)
        self.align = None
        self.alt = meta.alt
        self.attr_alt = meta.alt or meta.caption
        self.attr_title = meta.title or meta.caption
        self.caption = meta.caption
        self.copyright = meta.copyrights
        self.image = image
        self.image_group = image_group.uniqueId
        self.image_pattern = 'default'
        self.layout = ''
        self.src = self.uniqueId = image.uniqueId
        self.title = meta.title
        self.uniqueId = image.uniqueId


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
class TopicLink(object):
    """Filter and restructure all topiclinks and labels
    :rtype: generator
    """

    def __init__(self, centerpage):
        self.centerpage = centerpage

    def __iter__(self):
        for i in xrange(1, 4):
            label = getattr(self.centerpage, 'topiclink_label_%s' % i, None)
            link = getattr(self.centerpage, 'topiclink_url_%s' % i, None)
            if label is not None and link is not None:
                yield (label, link)
