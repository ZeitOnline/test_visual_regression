from grokcore.component import adapter, implementer
from zeit.content.image.interfaces import IImageGroup, IImage,  IImageMetadata
import zeit.cms.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces
import zeit.frontend.block
import zeit.frontend.interfaces

def auto_select_asset(teaser):
    video = get_video_asset(teaser)
    gallery = get_gallery_asset(teaser)
    image = get_image_asset(teaser)

    if video is not None:
        return video
    if gallery is not None:
        return gallery
    if image is not None:
        return image


def get_video_asset(teaser):
    video = zeit.content.video.interfaces.IVideoAsset(teaser)
    if video.video_2 is not None and video.video is not None:
        return [video.video, video.video_2]
    return video.video


def get_gallery_asset(teaser):
    gallery = zeit.content.gallery.interfaces.IGalleryReference(teaser)
    return gallery.gallery

def get_image_asset(teaser):
    image = zeit.content.image.interfaces.IImages(teaser)
    return image.image


@implementer(zeit.frontend.interfaces.ITeaserImage)
@adapter(IImageGroup, IImage)
class TeaserImage(zeit.frontend.block.BaseImage):

    def __init__(self, image_group, image):
        meta = IImageMetadata(image_group)
        self.align = None
        self.caption = meta.caption
        self.image = image
        self.layout = ''
        self.src = image.uniqueId
        self.uniqueId = image.uniqueId
        self.attr_title = meta.title
        self.title = meta.title
        self.attr_alt = meta.alt
        self.alt = meta.alt
        self.copyright = meta.copyrights
