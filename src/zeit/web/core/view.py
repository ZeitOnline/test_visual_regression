# -*- coding: utf-8 -*-
import datetime
import logging

import babel.dates
import pyramid.response
import pyramid.view
import requests

import zeit.cms.workflow.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.date

log = logging.getLogger(__name__)


class MetaView(type):

    """Meta class for view callables that ensures the return type is a dict."""

    def __new__(cls, name, bases, dct):
        def ensure_dict(func):
            def wrapped(self):
                v = func(self)
                return {} if v is None else v
            return wrapped
        dct['__call__'] = ensure_dict(dct.get('__call__', lambda self: {}))
        return super(MetaView, cls).__new__(cls, name, bases, dct)


class Base(object):

    """Base class for all views."""

    __metaclass__ = MetaView

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.response.cache_expires(300)
        self.request.response.headers.add(
            'X-ZMOVersion', self.request.registry.settings.zmo_version)

    @zeit.web.reify
    def type(self):
        return type(self.context).__name__.lower()

    @zeit.web.reify
    def ressort(self):
        if self.context.ressort:
            return self.context.ressort.lower()
        else:
            return ''

    @zeit.web.reify
    def sub_ressort(self):
        if self.context.sub_ressort:
            return self.context.sub_ressort.lower()
        else:
            return ''

    @zeit.web.reify
    def banner_channel(self):
        channel = ''
        if self.ressort:
            myressort = self.ressort.replace('zeit-magazin', 'zeitmz')
            # TODO: End discrepancy between testing and live ressorts!
            myressort = myressort.replace('lebensart', 'zeitmz')
            channel += myressort
        if self.sub_ressort:
            channel += '/' + self.sub_ressort.replace('-', 'und', 1)
        channel += '/' + self.banner_type
        return channel

    @zeit.web.reify
    def banner_type(self):
        return self.type

    @zeit.web.reify
    def adwords(self):
        keywords = ['zeitonline']
        # TODO: End discrepancy between testing and live ressorts!
        if self.ressort in ['zeit-magazin', 'lebensart']:
            keywords.append('zeitmz')
        return keywords

    def banner(self, tile):
        try:
            return zeit.web.core.banner.banner_list[tile - 1]
        except IndexError:
            return

    @zeit.web.reify
    def js_vars(self):
        names = ('banner_channel', 'ressort', 'sub_ressort', 'type')
        return [(name, getattr(self, name, '')) for name in names]

    @zeit.web.reify
    def navigation(self):
        return zeit.web.core.navigation.navigation

    @zeit.web.reify
    def navigation_services(self):
        return zeit.web.core.navigation.navigation_services

    @zeit.web.reify
    def navigation_classifieds(self):
        return zeit.web.core.navigation.navigation_classifieds

    @zeit.web.reify
    def title(self):
        return self.context.title

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle

    @zeit.web.reify
    def pagetitle(self):
        try:
            seo = zeit.seo.interfaces.ISEO(self.context)
            if seo.html_title:
                return seo.html_title
        except TypeError:
            pass
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        tokens = (self.supertitle, self.title)
        return ': '.join([t for t in tokens if t]) or default

    @zeit.web.reify
    def pagedescription(self):
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        try:
            seo = zeit.seo.interfaces.ISEO(self.context)
        except TypeError:
            return default
        if seo.html_description:
            return seo.html_description
        if self.context.subtitle:
            return self.context.subtitle
        return default

    @zeit.web.reify
    def rankedTags(self):
        return self.context.keywords

    @zeit.web.reify
    def rankedTagsList(self):
        if self.rankedTags:
            return ';'.join([rt.label for rt in self.rankedTags])
        else:
            default_tags = [self.context.ressort, self.context.sub_ressort]
            return ';'.join([dt for dt in default_tags if dt])

    @zeit.web.reify
    def is_hp(self):
        try:
            return self.request.path == (
                '/' + self.request.registry.settings.hp)
        except AttributeError:
            return False

    @zeit.web.reify
    def iqd_mobile_settings(self):
        iqd_ids = zeit.web.core.banner.iqd_mobile_ids
        if self.is_hp:
            return getattr(iqd_ids['hp'], 'centerpage')
        try:
            return getattr(iqd_ids[self.sub_ressort], self.type,
                           getattr(iqd_ids[self.sub_ressort], 'default'))
        except KeyError:
            return {}


class Content(Base):
    _navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo',
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2',
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3',
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4',
        )
    }

    is_longform = False

    @zeit.web.reify
    def subtitle(self):
        return self.context.subtitle

    @zeit.web.reify
    def show_article_date(self):
        return self.date_last_published_semantic or self.date_first_released

    @zeit.web.reify
    def date_first_released(self):
        tz = babel.dates.get_timezone('Europe/Berlin')
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @zeit.web.reify
    def date_first_released_meta(self):
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_first_released
        if date:
            return date.isoformat()

    @zeit.web.reify
    def date_last_published_semantic(self):
        tz = babel.dates.get_timezone('Europe/Berlin')
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_last_published_semantic
        if self.date_first_released is not None and date is not None:
            if date > self.date_first_released:
                return date.astimezone(tz)

    @zeit.web.reify
    def date_format(self):
        if self.context.product:
            if self.context.product.id in ('ZEI', 'ZMLB'):
                return 'short'
        return 'long'

    @zeit.web.reify
    def show_date_format(self):
        if self.date_last_published_semantic:
            return 'long'
        else:
            return self.date_format

    @zeit.web.reify
    def show_date_format_seo(self):
        return self.date_format

    @zeit.web.reify
    def breadcrumb(self):
        crumb = self._navigation
        l = [crumb['start']]
        l.append(crumb['zmo'])
        if self.context.ressort in crumb:
            l.append(crumb[self.context.ressort])
        if self.context.sub_ressort in crumb:
            l.append(crumb[self.context.sub_ressort])
        if self.title:
            l.append((self.title, ''))
        return l

    @zeit.web.reify
    def adwords(self):
        keywords = super(Content, self).adwords
        if self.is_top_of_mind:
            keywords.append('ToM')
        return keywords

    @zeit.web.reify
    def is_top_of_mind(self):
        return self.is_lead_story

    @zeit.web.reify
    def is_lead_story(self):
        tz = babel.dates.get_timezone('Europe/Berlin')
        today = datetime.datetime.now(tz).date()
        yesterday = (today - datetime.timedelta(days=1))

        if self.leadtime.start:
            # start = today
            if self.leadtime.start.date() == today:
                return True
            # start = yesterday and no end
            elif (self.leadtime.start.date() == yesterday
                  and not self.leadtime.end):
                return True
        if self.leadtime.end:
            # end = today
            if self.leadtime.end.date() == today:
                return True
        return False

    @zeit.web.reify
    def leadtime(self):
        try:
            return zeit.content.cp.interfaces.ILeadTime(self.context)
        except TypeError:
            return

    @zeit.web.reify
    def twitter_card_type(self):
        # TODO: use reasonable value depending on content type or template
        # summary_large_image, photo, gallery
        return 'summary_large_image'

    @zeit.web.reify
    def image_group(self):
        try:
            group = zeit.content.image.interfaces.IImages(self.context).image
            if zeit.content.image.interfaces.IImageGroup.providedBy(group):
                return group
        except TypeError:
            return


@pyramid.view.view_config(route_name='health_check')
def health_check(request):
    return pyramid.response.Response('OK', 200)


class service_unavailable(object):
    def __init__(self, context, request):
        log.exception('%s: %s at %s' % (context.__class__.__name__,
                      context.message, request.path))

    def __call__(self):
        try:
            body = requests.get('http://phpscripts.zeit.de/503.html',
                                timeout=4.0).text
        except requests.exceptions.RequestException:
            body = 'Status 503: Dokument zurzeit nicht verfügbar.'
        finally:
            return pyramid.response.Response(body, 503)


@pyramid.view.notfound_view_config(request_method='GET')
def not_found(request):
    try:
        body = requests.get('http://www.zeit.de/error/404',
                            timeout=4.0).text
    except requests.exceptions.RequestException:
        body = 'Status 404: Dokument nicht gefunden.'
    finally:
        return pyramid.response.Response(body, 404)


# For some reason we are not able to register ICMSContent on this.
# We have to register this on every content-view.
@pyramid.view.view_config(context=zeit.content.cp.interfaces.ICenterPage)
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.gallery.interfaces.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
def generate_render_with_header(context, request):
    return pyramid.response.Response(
        'OK', 200, headerlist=[('X-render-with', 'default')])


@pyramid.view.view_config(route_name='json_delta_time', renderer='json')
def json_delta_time(request):
    unique_id = request.GET.get('unique_id', None)
    date = request.GET.get('date', None)
    base_date = request.GET.get('base_date', None)
    if unique_id is not None:
        return json_delta_time_from_unique_id(request, unique_id, base_date)
    elif date is not None:
        return json_delta_time_from_date(date, base_date)
    else:
        return pyramid.response.Response(
            'Missing parameter: uniqueId or date', 412)


def json_delta_time_from_date(date, base_date):
    parsed_date = zeit.web.core.date.parse_date(date)
    if parsed_date is None:
        return pyramid.response.Response(
            'Invalid parameter: date', 412)
    parsed_base_date = zeit.web.core.date.parse_date(base_date)
    dt = zeit.web.core.date.DeltaTime(parsed_date, parsed_base_date)
    return {'delta_time': {'time': dt.get_time_since_modification()}}


def json_delta_time_from_unique_id(request, unique_id, base_date):
    try:
        content = zeit.cms.interfaces.ICMSContent(unique_id)
        cp = zeit.web.site.view_centerpage.Centerpage(content, request)
    except TypeError:
        return pyramid.response.Response(
            'Invalid resource', 500)
    json_dt = {'delta_time': []}
    for teaser in cp.area_main:
        # 1. Try to get date_last_published_semantic
        # 2. Try to get date_last_published
        # 3. Default to None
        mod_date = getattr(
            zeit.cms.workflow.interfaces.IPublishInfo(teaser[1]),
            'date_last_published_semantic', getattr(
                zeit.cms.workflow.interfaces.IPublishInfo(teaser[1]),
                'date_last_published', None))
        if mod_date is None:
            continue
        dt = zeit.web.core.date.DeltaTime(mod_date.replace(tzinfo=None))
        json_dt['delta_time'].append(
            {teaser[1].uniqueId: {'time': dt.get_time_since_modification()}})
    return json_dt
