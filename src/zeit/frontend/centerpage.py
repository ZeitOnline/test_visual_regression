import zeit.cms.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces

def auto_select_asset(teaser):
    gallery = zeit.content.gallery.interfaces.IGalleryReference(teaser)
    video =  zeit.content.video.interfaces.IVideoAsset(teaser)
    image = zeit.content.image.interfaces.IImages(teaser)

    if video.video_2 is not None and video.video is not None:
        return [video.video, video.video_2]
    if video.video is not None: return video.video
    if gallery.gallery is not None: return gallery.gallery
    if image is not None: return image.image
