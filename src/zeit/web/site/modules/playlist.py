import logging

import zeit.web
import zeit.web.core.block

log = logging.getLogger(__name__)


@zeit.web.register_module('playlist')
class Playlist(zeit.web.core.block.Module):
    """Implements the videostage a.k.a. *Der Videoriegel*.
    Makes use of the playlist module from Vivi. """

    @zeit.web.reify
    def videos(self):
        return self.context.referenced_playlist.videos
