import datetime

import grokcore.component
import pytz

import zeit.content.image.interfaces
import zeit.content.video.interfaces

import zeit.web.core.image


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
