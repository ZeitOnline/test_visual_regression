from grokcore.component import adapter, implementer

import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.frontend.block
import zeit.frontend.interfaces


def get_all_assets(teaser):
    assets = (get_video_asset(teaser),
              get_gallery_asset(teaser),
              get_image_asset(teaser))
    return tuple(a for a in assets if a)


def auto_select_asset(teaser):
    assets = get_all_assets(teaser)
    if len(assets):
        return assets[0]
    return None


def get_video_asset(teaser):
    video = zeit.content.video.interfaces.IVideoAsset(teaser)

    if video.video is not None:
        video.video.highest_rendition = _get_video_source(video.video)

    if video.video_2 is not None and video.video is not None:
        video.video_2.highest_rendition = _get_video_source(video.video_2)
        return [video.video, video.video_2]

    return video.video


def _get_video_source(self):
    try:
        highest_rendition = self.renditions[0]
        for rendition in self.renditions:
            if highest_rendition.frame_width < rendition.frame_width:
                highest_rendition = rendition
        return highest_rendition.url
    except (AttributeError, IndexError, TypeError):
        return self.flv_url


def get_gallery_asset(teaser):
    gallery = zeit.content.gallery.interfaces.IGalleryReference(teaser)
    return gallery.gallery


def get_image_asset(teaser):
    image = zeit.content.image.interfaces.IImages(teaser)
    return image.image


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
            sub_seq = zeit.frontend.interfaces.ITeaserSequence(item)
            self.sequence += sub_seq.sequence
            self.refs += sub_seq.refs
            return
        except TypeError:
            pass
        try:
            self.sequence.append(zeit.frontend.centerpage.Teaser(
                self.context, item))
            self.refs.append(self.context)
        except TypeError:
            pass


@implementer(zeit.frontend.interfaces.ITeaserSequence)
@adapter(list)
class TeaserList(TeaserSequence):

    def __init__(self, context):
        super(TeaserList, self).__init__(context)
        for item in iter(context):
            self._resolve_child(item)


@implementer(zeit.frontend.interfaces.ITeaserSequence)
@adapter(zeit.content.cp.interfaces.ITeaserBlock)
class TeaserBlock(TeaserList):

    pass


@implementer(zeit.frontend.interfaces.ITeaserSequence)
@adapter(zeit.content.cp.interfaces.IAutoPilotTeaserBlock)
class AutoPilotTeaserBlock(TeaserBlock):

    pass


@implementer(zeit.frontend.interfaces.ITeaserSequence)
@adapter(dict)
class TeaserDict(TeaserSequence):

    def __init__(self, context):
        super(TeaserDict, self).__init__(context)
        for item in context.itervalues():
            self._resolve_child(item)


@implementer(zeit.frontend.interfaces.ITeaserSequence)
@adapter(zeit.content.cp.interfaces.ITeaserBar)
class TeaserBar(TeaserDict):

    pass


@implementer(zeit.frontend.interfaces.ITeaser)
@adapter(TeaserSequence, zeit.cms.interfaces.ICMSContent)
class Teaser(object):

    def __init__(self, block, context):
        self.video = None
        self.gallery = None
        self.image = zeit.frontend.template.get_teaser_image(block, context)
        self.context = context


@implementer(zeit.frontend.interfaces.ITeaserImage)
@adapter(zeit.content.image.interfaces.IImageGroup,
         zeit.content.image.interfaces.IImage)
class TeaserImage(zeit.frontend.block.BaseImage):

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
        self.layout = ''
        self.src = image.uniqueId
        self.title = meta.title
        self.uniqueId = image.uniqueId
