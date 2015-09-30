import logging

import zeit.content.video.interfaces

import zeit.web
import zeit.web.site.module

log = logging.getLogger(__name__)


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
