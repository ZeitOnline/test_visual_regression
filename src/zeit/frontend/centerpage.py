import zeit.cms.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces


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

