import datetime

import grokcore.component
import pytz

import zeit.content.video.interfaces

import zeit.web.core.image


class VideoExpiration(zeit.web.core.image.ImageExpiration):

    grokcore.component.context(zeit.content.video.interfaces.IVideo)

    @property
    def seconds(self):
        if self.context.expires is None:
            return None
        now = datetime.datetime.now(pytz.UTC)
        return int((self.context.expires - now).total_seconds())
