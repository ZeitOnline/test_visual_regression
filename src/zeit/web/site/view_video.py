import logging

import pyramid.view
import babel.dates
import pyramid.httpexceptions
import pyramid.view

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

    def __init__(self, context, request):
        super(Video, self).__init__(context, request)
        if self.request.headers.get('X-SEO-Slug', '') != self.seo_slug:
            location = '{}/{}'.format(self.content_url, self.seo_slug)
            if self.request.query_string:
                location = '{}?{}'.format(location, self.request.query_string)
            raise pyramid.httpexceptions.HTTPMovedPermanently(location)

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
            return

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
    def webtrekk_assets(self):
        return ['video.0/seite-1']

    @zeit.web.reify
    def seo_slug(self):
        return self.context.seo_slug

    @zeit.web.reify
    def og_url(self):
        return '{}/{}'.format(self.content_url, self.seo_slug)

    @zeit.web.reify
    def product_id(self):
        return super(Video, self).product_id or 'zede'
