import logging

import grokcore.component

import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.core.centerpage

log = logging.getLogger(__name__)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    def __init__(self, context):
        super(ImageGroup, self).__init__(context)
        self.image_url = context.video_still
        self.uniqueId = '{}/imagegroup/'.format(context.uniqueId)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImages(zeit.web.core.image.RemoteImages):
    pass


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

    product_configuration = 'zeit.web'
    config_url = 'series-source'

    def getValues(self):
        try:
            tree = self._get_tree()
        except (TypeError, IOError):
            return []
        videoseries = tree.xpath('/allseries/videoseries/series')
        result = []
        for node in videoseries:
            result.append(dict(url=node.get('url'), title=node.get('title')))
        return result

VIDEO_SERIES_SOURCE = VideoSeriesSource()
