from grokcore.component import adapter, implementer
from zeit.content.image.interfaces import IImageGroup, IImage, IImageMetadata
from zeit.content.video.interfaces import IVideo
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
    except AttributeError:
        return self.flv_url
    except TypeError:
        return self.flv_url

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
