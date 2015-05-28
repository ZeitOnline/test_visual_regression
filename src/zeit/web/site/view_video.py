import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
import babel.dates

import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.date
import zeit.web.core.view
import zeit.web.site.view


log = logging.getLogger(__name__)


@view_defaults(context=zeit.content.video.interfaces.IVideo,
               custom_predicates=(zeit.web.site.view.is_zon_content,),
               request_method='GET')
@view_config(renderer='templates/video.html')
class Video(zeit.web.core.view.Content, zeit.web.site.view.Base):

    @zeit.web.reify
    def image_group(self):
        return zeit.content.image.interfaces.IImageGroup(self.context)

    @zeit.web.reify
    def video_still(self):
        return self.image_group['still.jpg']

    @zeit.web.reify
    def _seconds(self):
        try:
            return self.context.renditions[0].video_duration / 1000
        except (AttributeError, IndexError, TypeError):
            pass

    @zeit.web.reify
    def duration(self):
        if self._seconds:
            return babel.dates.format_timedelta(
                babel.dates.timedelta(seconds=self._seconds),
                threshold=1, locale=zeit.web.core.date.locale)

    @zeit.web.reify
    def iso_duration(self):
        if self._seconds:
            return 'PT{}S'.format(self._seconds)

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle or self.context.teaserSupertitle

    @zeit.web.reify
    def title(self):
        return self.context.title or self.context.teaserTitle

    @zeit.web.reify
    def subtitle(self):
        return self.context.subtitle or self.context.teaserText
