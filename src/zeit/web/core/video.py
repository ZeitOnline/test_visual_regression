import datetime

import grokcore.component
import pytz

import zeit.cms.interfaces
import zeit.content.video.interfaces

import zeit.web.core.image


def get_seo_slug(context):
    titles = (t for t in (context.supertitle, context.title) if t)
    return zeit.cms.interfaces.normalize_filename(u' '.join(titles))


class VideoExpiration(zeit.web.core.image.ImageExpiration):

    grokcore.component.context(zeit.content.video.interfaces.IVideo)

    @property
    def seconds(self):
        if self.context.expires is None:
            return None
        now = datetime.datetime.now(pytz.UTC)
        return int((self.context.expires - now).total_seconds())
