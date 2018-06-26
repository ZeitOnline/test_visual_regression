import logging

import zeit.cms.content.sources

import zeit.web
import zeit.web.core.centerpage

log = logging.getLogger(__name__)


@zeit.web.register_module('playlist')
class Playlist(zeit.web.core.centerpage.Module):
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
        return list(VIDEO_SERIES_SOURCE)


class VideoSeriesSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.cms'
    config_url = 'source-serie'

    def getValues(self):
        try:
            tree = self._get_tree()
        except (TypeError, IOError):
            return []
        videoseries = tree.xpath('//series[@video="yes"]')
        result = []
        for node in videoseries:
            result.append(dict(url=node.get('url'), title=node.get('title')))
        return result

VIDEO_SERIES_SOURCE = VideoSeriesSource()
