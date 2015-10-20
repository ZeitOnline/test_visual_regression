import logging

import grokcore.component

import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.site.module

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class ImageGroup(zeit.web.core.image.LocalImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.video_still
        self.uniqueId = '{}/imagegroup/'.format(context.uniqueId)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImages(object):

    def __init__(self, context):
        self.context = context
        self.image = zeit.content.image.interfaces.IImageGroup(context)


@zeit.web.register_module('playlist')
class Playlist(zeit.web.site.module.Module):
    """Implements the videostage a.k.a. *Der Videoriegel*.
    Makes use of the playlist module from Vivi. """

    @zeit.web.reify
    def videos(self):
        if not zeit.content.video.interfaces.IPlaylist.providedBy(
                self.context.referenced_playlist):
            return []
        return self.context.referenced_playlist.videos

    @zeit.web.reify
    def video_series_list(self):
        return zeit.web.core.sources.video_series
