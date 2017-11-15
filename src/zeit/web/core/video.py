import datetime

import grokcore.component
import pytz

import zeit.brightcove.connection
import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web.core.cache
import zeit.web.core.image
import zeit.web.core.metrics


LONG_TERM_CACHE = zeit.web.core.cache.get_region('long_term')


@grokcore.component.implementer(zeit.content.image.interfaces.IImageGroup)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class ImageGroup(zeit.web.core.image.RemoteImageGroup):

    @classmethod
    def get_image_url(cls, context):
        return context.video_still

    @zeit.web.reify
    def uniqueId(self):
        return '{}/imagegroup/'.format(self.context.uniqueId)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.content.video.interfaces.IVideo)
class VideoImages(zeit.web.core.image.RemoteImages):
    pass


class VideoExpiration(zeit.web.core.image.ImageExpiration):

    grokcore.component.context(zeit.content.video.interfaces.IVideo)

    @property
    def seconds(self):
        if self.context.expires is None:
            return None
        now = datetime.datetime.now(pytz.UTC)
        return int((self.context.expires - now).total_seconds())


@LONG_TERM_CACHE.cache_on_arguments()
def get_video_with_caching(self, id):
    with zeit.web.core.metrics.timer(
            'zeit.web.core.video.brightcove.playback.http.reponse_time'):
        return original_get_video(self, id)
original_get_video = zeit.brightcove.connection.PlaybackAPI.get_video
zeit.brightcove.connection.PlaybackAPI.get_video = get_video_with_caching
