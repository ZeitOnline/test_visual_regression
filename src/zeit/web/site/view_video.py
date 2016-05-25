import logging

import pyramid.view
import babel.dates
import pyramid.httpexceptions
import pyramid.view

import zeit.cms.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.date
import zeit.web.core.view
import zeit.web.site.view


log = logging.getLogger(__name__)


@pyramid.view.view_config(
    context=zeit.content.video.interfaces.IVideo,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_method='GET',
    renderer='templates/video.html')
class Video(zeit.web.core.view.Content, zeit.web.site.view.Base):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.banner_on
        if 'X-SEO-Slug' in self.request.headers and (
                self.request.headers['X-SEO-Slug'] != self.slug):
            location = '{}/{}'.format(self.content_url, self.slug)
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=location)

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Video, self).breadcrumbs
        breadcrumbs.extend([('Video', 'http://xml.zeit.de/video/index')])
        self.breadcrumbs_by_navigation(breadcrumbs)
        self.breadcrumbs_by_title(breadcrumbs)
        return breadcrumbs

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

    @zeit.web.reify
    def webtrekk_assets(self):
        return ['video.0/seite-1']

    @zeit.web.reify
    def slug(self):
        return self.get_slug(self)

    @staticmethod
    def get_slug(self):
        titles = (t for t in (self.supertitle, self.title) if t)
        return zeit.cms.interfaces.normalize_filename(u' '.join(titles))
