# -*- coding: utf-8 -*-
from __future__ import absolute_import

import base64
import collections
import datetime
import logging
import os.path
import urlparse
import re

import babel.dates
import bugsnag
import pyramid.response
import pyramid.settings
import pyramid.view
import pyramid.httpexceptions
import zope.component

import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.push.interfaces

from zeit.web.core.source import LIGATUS_BLACKLIST
import zeit.web
import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.core.cache
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.navigation
import zeit.web.core.paywall
import zeit.web.core.template


SHORT_TERM_CACHE = zeit.web.core.cache.get_region('short_term')
DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')
log = logging.getLogger(__name__)


def known_content(resource):
    return (zeit.content.article.interfaces.IArticle.providedBy(resource) or
            zeit.content.gallery.interfaces.IGallery.providedBy(resource) or
            zeit.content.video.interfaces.IVideo.providedBy(resource))


def is_advertorial(context, request):
    product = getattr(context, 'product', None)
    return getattr(product, 'title', None) == 'Advertorial'


def is_paginated(context, request):
    # XXX: We need some form of IPagination to evaluate wheter or not a context
    # is paginated. This is, however, not possible at the moment, because the
    # current evaluation of IPagination of an area level is not efficient.
    # (RD, 2015-06-02)
    try:
        return int(request.GET['p']) > 1
    except (KeyError, ValueError):
        return False


def is_not_in_production(context, request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return ((conf.get('environment') != 'production') or
            (request.client_addr == '127.0.0.1'))


def redirect_on_trailing_slash(request):
    if request.path.endswith('/') and not len(request.path) == 1:
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(
            request.url)
        url = '{}://{}{}'.format(scheme, netloc, path[:-1])
        url = url if query == '' else '{}?{}'.format(url, query)
        raise pyramid.httpexceptions.HTTPMovedPermanently(
            location=url)


def is_paywalled(context, request):
    return zeit.web.core.paywall.Paywall.status(request)


class Base(object):

    """Base class for all views."""

    seo_title_default = u''
    pagetitle_suffix = u''
    inline_svg_icons = False

    def __call__(self):
        redirect_on_trailing_slash(self.request)

        # Set caching times.
        client_time = zeit.web.core.interfaces.ICachingTime(self.context)
        varnish_time = zeit.web.core.interfaces.IVarnishCachingTime(
            self.context)
        if varnish_time < client_time:
            varnish_time = client_time
        self.request.response.cache_expires(client_time)
        self.request.response.headers.add('X-Maxage', str(varnish_time))

        # Set zeit.web version header
        try:
            self.request.response.headers.add(
                'X-Version', self.request.registry.settings.version)
            self.request.response.headers.add(
                'Surrogate-Key',
                self.context.uniqueId.encode("iso-8859-1", "replace"))
        except AttributeError:
            pass

        return {}

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._webtrekk_assets = []

    @zeit.web.reify
    def vgwort_url(self):
        token = zeit.vgwort.interfaces.IToken(self.context).public_token
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if token and conf.get('vgwort_url'):
            return '{}/{}'.format(conf.get('vgwort_url'), token)

    @zeit.web.reify
    def type(self):
        return type(self.context).__name__.lower()

    @zeit.web.reify
    def tracking_type(self):
        return self.type

    # XXX Base View should not depend on ICommonMetadata
    # Throws an error if resssort, sub_ressort, cap_title ... is None
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
    def channels(self):
        """ A string with a semicolon seperated list of all channels """
        channels = getattr(self.context, 'channels', None)
        if isinstance(channels, (list, tuple)):
            channel_list = [item for tuples in channels for item in tuples]
            return ';'.join(zeit.web.core.template.format_webtrekk(str(
                item)) for item in channel_list if item is not None)

    @zeit.web.reify
    def is_advertorial(self):
        return is_advertorial(self.context, self.request)

    @zeit.web.reify
    def serie(self):
        if self.context.serie is None:
            return ''
        return self.context.serie.serienname

    @zeit.web.reify
    def series_title(self):
        series = zeit.web.core.interfaces.ISeries(self.context, [])
        try:
            return series.title
        except AttributeError:
            return True

    @zeit.web.reify
    def podcastseries_feed(self):
        series = zeit.web.core.interfaces.ISeries(self.context, [])
        try:
            return series.podcastseries_feed.replace("-", "")
        except AttributeError:
            return True

    @zeit.web.reify
    def is_podcastseries(self):
        series = zeit.web.core.interfaces.ISeries(self.context, [])
        try:
            return series.kind == "Podcast"
        except AttributeError:
            return None

    @zeit.web.reify
    def cap_title(self):
        if not self.context.cap_title:
            return 'Anzeige'
        return self.context.cap_title.title()

    @zeit.web.reify
    def path_info(self):
        return self.request.path_info

    @zeit.web.reify
    def package(self):
        return '.'.join(self.__class__.__module__.split('.')[:3])

    @zeit.web.reify
    def banner_channel(self):
        # manually banner_id rules first
        if self.context.banner_id is not None:
            return u'{}/{}'.format(self.context.banner_id, self.banner_type)
        # execption: 'reisen' now is 'entdecken'
        if self.ressort == 'entdecken':
            return u'reisen/{}'.format(self.banner_type)
        # exeption: angebote are mapped with two levels
        if self.is_advertorial or self.ressort == 'angebote':
            adv_title = self.context.advertisement_title or self.ressort
            return u'{}/{}/{}'.format(
                'adv',
                "".join(re.findall(r"[A-Za-z0-9_]*", adv_title)).lower(),
                self.banner_type)
        # execption: campus pages
        if self.package == 'zeit.web.campus':
            topiclabel = getattr(self, 'topic_label', '')
            topiclabel = zeit.web.core.template.format_iqd(topiclabel)
            return u'{}/{}/{}/{}'.format(
                'campus',
                'thema' if topiclabel else '',
                topiclabel or '',
                self.banner_type)
        # mapping by config
        mappings = zeit.web.core.banner.BANNER_ID_MAPPINGS_SOURCE
        for mapping in mappings:
            if getattr(self, mapping['target'], None) == mapping['value']:
                # change ressort but leave subressort intact
                if mapping['target'] == 'ressort' and self.sub_ressort != '':
                    return u'{}/{}/{}'.format(
                        mapping['banner_code'],
                        self.sub_ressort, self.banner_type)
                else:
                    return u'{}/{}'.format(mapping['banner_code'],
                                           self.banner_type)
        # subressort and ressort ?
        if self.sub_ressort != '' and self.ressort != '':
            return u'{}/{}/{}'.format(self.ressort,
                                      self.sub_ressort, self.banner_type)
        # ressort ?
        if self.ressort != '':
            return u'{}/{}'.format(self.ressort, self.banner_type)
        # fallback of the fallbacks
        return u'vermischtes/{}'.format(self.banner_type)

    @zeit.web.reify
    def banner_type(self):
        return self.type

    @zeit.web.reify
    def advertising_enabled(self):
        if self.context.banner is False:
            return False
        else:
            return True

    @zeit.web.reify
    def advertising_in_article_body_enabled(self):
        if self.context.banner_content is False:
            return False
        else:
            return self.advertising_enabled

    @zeit.web.reify
    def adcontroller_handle(self):
        suffix = '_trsf'
        replacements = {
            'article': 'artikel',
            'author': 'centerpage',
            'centerpage': 'centerpage',
            'gallery': 'galerie',
            'quiz': 'quiz',
            'video': 'video_artikel'}
        if self.is_hp:
            return 'homepage{}'.format(suffix)
        if self.is_advertorial:
            return '{}_{}{}'.format(
                'mcs' if 'mcs/' in self.banner_channel else 'adv',
                'index' if self.type == 'centerpage' else 'artikel',
                suffix)
        if self.type == 'centerpage' and (
                self.sub_ressort == '' or self.ressort == 'zeit-magazin'):
            return 'index{}'.format(suffix)
        if self.type in replacements:
            return '{}{}'.format(replacements[self.type], suffix)
        return 'centerpage{}'.format(suffix)

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore."""
        # remove type from banner code string and split
        levels = self.banner_channel.replace(
            '/{}'.format(self.type), '').split('/')
        level2 = "".join(re.findall(r"[A-Za-z0-9_]*", levels[0]))
        level3 = "".join(re.findall(r"[A-Za-z0-9_]*", levels[1])) if len(
            levels) > 1 else ''
        level4 = "".join(re.findall(r"[A-Za-z0-9_]*", levels[2])) if len(
            levels) > 2 else ''
        keywords = ','.join(self.adwords + self.adc_keywords[:6]) if (
            level2 != 'angebote') else '{},{}'.format(level2, level3)
        return [('$handle', self.adcontroller_handle),
                ('level2', level2),
                ('level3', level3),
                ('level4', level4),
                ('$autoSizeFrames', True),
                ('keywords', keywords),
                ('tma', '')]

    @zeit.web.reify
    def meta_robots(self):
        seo = zeit.seo.interfaces.ISEO(self.context, None)
        if seo and seo.meta_robots:
            return seo.meta_robots
        return 'index,follow,noarchive'

    @zeit.web.reify
    def adwords(self):
        return ['zeitonline']

    @zeit.web.reify
    def canonical_url(self):
        """ Set own url as default canonical. Overwrite for special
            cases and page types"""
        return u"{}{}".format(
            self.request.route_url('home').rstrip('/'), self.request.path_info)

    @zeit.web.reify
    def js_vars(self):
        names = ('banner_channel', 'ressort', 'sub_ressort', 'type',
                 'update_signals_comments_interval',
                 'update_signals_time_interval', 'paywall')
        return [(name, getattr(self, name, '')) for name in names]

    @zeit.web.reify
    def js_toggles(self):
        toggles = zeit.web.core.application.FEATURE_TOGGLES
        names = ('update_signals', 'https', 'track_gate_visibility')
        return [(name, toggles.find(name)) for name in names]

    @zeit.web.reify
    def navigation(self):
        return zeit.web.core.navigation.NAVIGATION_SOURCE.navigation

    @zeit.web.reify
    def navigation_services(self):
        return zeit.web.core.navigation.NAVIGATION_SERVICES_SOURCE.navigation

    @zeit.web.reify
    def navigation_classifieds(self):
        src = zeit.web.core.navigation.NAVIGATION_CLASSIFIEDS_SOURCE
        return src.navigation

    @zeit.web.reify
    def navigation_footer_publisher(self):
        src = zeit.web.core.navigation.NAVIGATION_FOOTER_PUBLISHER_SOURCE
        return src.navigation

    @zeit.web.reify
    def navigation_footer_links(self):
        src = zeit.web.core.navigation.NAVIGATION_FOOTER_LINKS_SOURCE
        return src.navigation

    @zeit.web.reify
    def navigation_more(self):
        src = zeit.web.core.navigation.NAVIGATION_MORE_SOURCE
        return src.navigation

    @zeit.web.reify
    def title(self):
        if not self.context.title:
            return ''
        return self.context.title.strip()

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle

    @zeit.web.reify
    def subtitle(self):
        return self.context.subtitle

    def _pagetitle(self, suffix):
        try:
            title = zeit.seo.interfaces.ISEO(self.context).html_title
            assert title
        except (AssertionError, TypeError):
            if getattr(self, 'supertitle'):
                title = u'{}: {}'.format(self.supertitle, self.title)
            else:
                title = self.title
        if title:
            if self.is_hp or not suffix:
                return title
            else:
                return title + self.pagetitle_suffix
        return self.seo_title_default

    @zeit.web.reify
    def pagetitle(self):
        return self._pagetitle(suffix=True)

    @zeit.web.reify
    def social_pagetitle(self):
        return self._pagetitle(suffix=False)

    @zeit.web.reify
    def social_description(self):
        return self.pagedescription

    @zeit.web.reify
    def pagedescription(self):
        try:
            desc = zeit.seo.interfaces.ISEO(self.context).html_description
            assert desc
        except (AssertionError, TypeError):
            desc = self.context.subtitle
        return desc or self.seo_title_default

    @zeit.web.reify
    def keywords(self):
        return zeit.web.core.article.get_keywords(self.context)

    @zeit.web.reify
    def meta_keywords(self):
        if self.keywords:
            result = [x.label for x in self.keywords]
        else:
            result = [self.ressort.title(), self.sub_ressort.title()]
        return [x for x in result if x]

    @zeit.web.reify
    def adc_keywords(self):
        lowercase = [x.label.lower() for x in self.keywords if x.label]
        return ["".join(re.findall(r"\w", item)) for item in lowercase]

    @zeit.web.reify
    def is_hp(self):
        try:
            return self.request.path == ('/{}'.format(
                self.request.registry.settings.hp))
        except AttributeError:
            return False

    @zeit.web.reify
    def is_wrapped(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        try:
            return ('ZONApp' in self.request.headers.get('user-agent', '') or (
                conf.get('environment') != 'production' and
                    'app-content' in self.request.query_string))
        except (AttributeError, TypeError):
            return False

    @zeit.web.reify
    def product_id(self):
        try:
            return self.context.product.id
        except AttributeError:
            return None

    @zeit.web.reify
    def detailed_content_type(self):
        return zeit.web.core.interfaces.IDetailedContentType(self.context)

    @zeit.web.reify
    def breaking_news(self):
        return zeit.web.core.block.BreakingNews()

    @zeit.web.reify
    def content_path(self):
        return u'/' + u'/'.join(self.request.traversed)

    @zeit.web.reify
    def content_url(self):
        return self.request.route_url('home').rstrip('/') + self.content_path

    @zeit.web.reify
    def og_url(self):
        return self.content_url

    @zeit.web.reify
    def timezone(self):
        return babel.dates.get_timezone('Europe/Berlin')

    @zeit.web.reify
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @zeit.web.reify
    def date_last_modified(self):
        return zeit.web.core.date.mod_date(self.context)

    @zeit.web.reify
    def date_first_released(self):
        date = self.publish_info.date_first_released
        if date:
            return date.astimezone(self.timezone)

    @zeit.web.reify
    def has_cardstack(self):
        return False

    @zeit.web.reify
    def newsletter_optin_tracking(self):
        return None

    @zeit.web.reify
    def shared_cardstack_id(self):
        return None

    @zeit.web.reify
    def cardstack_head(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('cardstack_backend', '').rstrip('/')
        stack_id = (u'/' + self.shared_cardstack_id if self.shared_cardstack_id
                    else u'')
        return url + u'/stacks' + stack_id + u'/esi/head'

    @zeit.web.reify
    def cardstack_body(self):
        # We use __STACK__ because {} or %s would not survive urlencoding
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('cardstack_backend', '').rstrip('/')
        return url + (u'/stacks/__STACK__/esi/body'
                      u'?shareUrlQuerySuffix=stackId%3D__STACK__')

    @zeit.web.reify
    def cardstack_scripts(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('cardstack_backend', '').rstrip('/')
        return url + u'/stacks/esi/scripts'

    @zeit.web.reify
    def breadcrumbs(self):
        return []

    def breadcrumbs_by_title(self, breadcrumbs=None):
        if breadcrumbs is None:
            breadcrumbs = []
        breadcrumbs.extend([(
            self.pagetitle.replace(self.pagetitle_suffix, ''), None)])
        return breadcrumbs

    def breadcrumbs_by_navigation(self, breadcrumbs=None):
        if breadcrumbs is None:
            breadcrumbs = []
        for segment in (self.ressort, self.sub_ressort):
            if segment == u'reisen':
                segment = u'reise'
            elif segment == u'studium':
                segment = u'campus'
            try:
                nav_item = zeit.web.core.navigation.NAVIGATION_SOURCE.by_name[
                    segment]
                if nav_item['text'] == 'Campus':
                    nav_item['text'] = 'ZEIT Campus'
                breadcrumbs.extend([(nav_item['text'], nav_item['link'])])
            except KeyError:
                # Segment is no longer part of the navigation
                next
        return breadcrumbs

    @zeit.web.reify
    def webtrekk(self):

        def get_param(key):
            value = getattr(self, key, False)
            return value.lower() if value else ''

        pagination = '1/1'
        if getattr(self, 'pagination', None):
            if getattr(self, 'is_all_pages_view', False):
                page = 'all'
            else:
                page = self.pagination.get('current')
            pagination = '{}/{}'.format(page, self.pagination.get('total'))

        push = zeit.push.interfaces.IPushMessages(self.context, '')
        if push:
            push = push.get(type='mobile') or {}
            push = push.get('payload_template') or ''
            push = push.replace('.json', '.push')

        if getattr(self, 'framebuilder_requires_webtrekk', False):
            pagetype = 'centerpage.framebuilder'
        elif zeit.web.core.article.IFAQArticle.providedBy(self.context):
            pagetype = 'article.faq'
        else:
            pagetype = self.detailed_content_type

        if zeit.cms.content.interfaces.ICommonMetadata.providedBy(
                self.context):
            access = self.context.access
        else:
            field = zeit.cms.content.interfaces.ICommonMetadata['access']
            access = field.default

        if access == 'registration':
            fcf = zeit.web.core.paywall.Paywall.first_click_free(self.request)
            first_click_free = 'yes' if fcf else 'no'
        else:
            first_click_free = 'unfeasible'

        content_group = collections.OrderedDict([
            ('cg1', 'redaktion'),  # Zuordnung/Bereich
            ('cg2', get_param('tracking_type')),  # Kategorie
            ('cg3', get_param('ressort')),  # Ressort
            ('cg4', get_param('product_id')),  # Online/Sourcetype
            ('cg5', self.sub_ressort.lower()),  # Subressort
            ('cg6', self.serie.replace(' ', '').lower()),  # Cluster
            ('cg7', self.request.path_info.split('/')[-1]),  # doc-path
            ('cg8', get_param('banner_channel')),  # Banner-Channel
            ('cg9', zeit.web.core.template.format_date(
                self.date_first_released,
                'short_num'))  # Veröffentlichungsdatum
        ])

        custom_parameter = collections.OrderedDict([
            ('cp1', get_param('authors_list')),  # Autor
            ('cp2', self.ivw_code),  # IVW-Code
            ('cp3', pagination),  # Seitenanzahl
            ('cp4', ';'.join(self.meta_keywords).lower()),  # Schlagworte
            ('cp5', self.date_last_modified),  # Last Published
            ('cp6', getattr(self, 'text_length', '')),  # Textlänge
            ('cp7', get_param('news_source')),  # Quelle
            ('cp8', get_param('product_id')),  # Product-ID
            ('cp9', get_param('banner_channel')),  # Banner-Channel
            ('cp10', ('no', 'yes')[self.advertising_enabled]),  # Banner aktiv
            ('cp11', ''),  # Fehlermeldung
            ('cp12', 'desktop.site'),  # Seitenversion Endgerät
            ('cp13', 'stationaer'),  # Breakpoint
            ('cp14', 'friedbert'),  # Beta-Variante
            ('cp15', push),  # Push und Eilmeldungen
            ('cp25', 'original'),  # Plattform
            ('cp26', pagetype),  # inhaltlicher Pagetype
            ('cp27', ';'.join(self.webtrekk_assets)),  # Asset
            ('cp28', access),  #
            ('cp29', first_click_free),  # First click free
            ('cp30', self.paywall or 'open'),  # Paywall Schranke
            ('cp32', 'unfeasible'),  # Protokoll (set via JS in webtrekk.html)
            ('cp38', self.channels or 'undefined')  # Channel-Liste
        ])

        if not zeit.web.core.application.FEATURE_TOGGLES.find(
                'reader_revenue'):
            custom_parameter['cp29'] = 'unfeasible'

        return {
            'contentGroup': content_group,
            'customParameter': custom_parameter
        }

    @zeit.web.reify
    def webtrekk_identifier(self):
        # @see https://sites.google.com/a/apps.zeit.de/
        # verpixelungskonzept-zeit-online/webtrekk#TOC-Struktur-der-Content-IDs
        identifier = '.'.join(map(zeit.web.core.template.format_webtrekk, [
            'redaktion', self.ressort, self.sub_ressort,
            self.serie.replace(' ', ''), self.type, self.product_id or '']))
        return identifier

    @zeit.web.reify
    def webtrekk_content_id(self):
        _, netloc, path, _, _, _ = urlparse.urlparse(
            self.content_url)
        return u'{}|{}{}'.format(self.webtrekk_identifier, netloc, path)

    @zeit.web.reify
    def webtrekk_assets(self):
        return self._webtrekk_assets

    def append_to_webtrekk_assets(self, value):
        self._webtrekk_assets.append(value)

    @zeit.web.reify
    def ivw_code(self):
        code = [self.ressort or 'administratives',
                self.sub_ressort,
                'bild-text']
        if zeit.web.core.template.zplus_abo_content(self.context) and (
                not self.paywall):
            code.append('paid')
        return '/'.join([x for x in code if x])

    @zeit.web.reify
    def no_overscrolling(self):
        if not getattr(self.context, 'overscrolling', None):
            return True

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT ONLINE'

    @zeit.web.reify
    def site_name(self):
        return self.publisher_name

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitonline'

    @zeit.web.reify
    def paywall(self):
        return zeit.web.core.paywall.Paywall.status(self.request)

    @zeit.web.reify
    def update_signals_comments_interval(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('update_signals_comments_interval', '')

    @zeit.web.reify
    def update_signals_time_interval(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('update_signals_time_interval', '')


class CommentMixin(object):

    def __call__(self):
        result = super(CommentMixin, self).__call__()
        if not self.comments_loadable:
            # XXX We can't get from cached function to its cache region, so we
            # need to duplicate it here from is_community_healthy().
            self.request.response.cache_expires(
                SHORT_TERM_CACHE.expiration_time)
        return result

    @zeit.web.reify
    def community(self):
        return zope.component.getUtility(zeit.web.core.interfaces.ICommunity)

    @zeit.web.reify
    def comments_loadable(self):
        return self.community.is_healthy()

    @zeit.web.reify
    def community_maintenance(self):
        return zeit.web.core.comments.community_maintenance()

    def show_replies(self, parent):
        # The request is a comment permalink, so we need to show the
        # replies of the permalinked comment's root comment.
        try:
            cid = int(self.request.GET['cid'])
        except (KeyError, ValueError):
            return False
        if not self.comments:
            return False

        permalinked = self.comments['index'].get(cid, {})
        if not (permalinked.get('is_reply') and permalinked.get('root_index')):
            return False
        try:
            root = self.comments['comments'][permalinked['root_index'] - 1]
            return root['cid'] == parent['cid']
        except IndexError:
            return False

    def _get_comment_sorting(self):
        # Basic comment sort is ascending.
        sort = 'asc'

        # This might be overwritten by context specific default.
        if getattr(self.context, 'recent_comments_first', False):
            sort = 'desc'

        # User might change sort order as well, but fall back to
        # derived default, if it hasn't.
        return self.request.params.get('sort', sort)

    @zeit.web.reify
    def comments(self):
        if not self.show_commentthread:
            return

        try:
            page = int(self.request.params.get('page', 1))
        except ValueError:
            return
        cid = self.request.params.get('cid', None)
        return self.community.get_thread(
            self.context.uniqueId,
            sort=self._get_comment_sorting(),
            page=page, cid=cid)

    def get_comment(self, cid):
        return self.community.get_comment(self.context.uniqueId, cid)

    @zeit.web.reify
    def commenting_allowed(self):
        return self.context.commentsAllowed and self.show_commentthread

    @zeit.web.reify
    def show_commentthread(self):
        return self.context.commentSectionEnable is not False

    @zeit.web.reify
    def article_premoderate(self):
        return self.context.commentsPremoderate

    @zeit.web.reify
    def has_comment_area(self):
        # show comments if:
        # 1. comment section is enabled *and*
        # 2. commenting is allowed _or_ there are existing comments
        # (avoid displaying "0 Comments: Add one" + "sorry, comments closed")
        # be carefull with self.comment_count - it sends an extra request
        # and is intended to be used _outside_ the comments ESI
        return self.show_commentthread and (self.commenting_allowed or
                                            self.comment_count)

    @zeit.web.reify
    def comment_form(self):
        user = self.request.user
        user_blocked = user.get('blocked')
        premoderation_user = user.get('premoderation')
        valid_community_login = (
            user.get('has_community_data') and
            user.get('uid') and user.get('uid') != '0')
        authenticated = user.get('ssoid')

        # used for general alerts in the comment section header
        message = None

        # used for general alerts or user specific alerts in the comment form
        note = None

        if self.community_maintenance['active']:
            message = self.community_maintenance['text_active']
        elif not self.comments_loadable:
            message = (u'Ein technischer Fehler ist aufgetreten. '
                       u'Die Kommentare zu diesem Artikel konnten '
                       u'nicht geladen werden. Bitte entschuldigen Sie '
                       u'diese Störung.')
        elif not self.commenting_allowed:
            message = (u'Der Kommentarbereich dieses Artikels ist geschlossen.'
                       u' Wir bitten um Ihr Verständnis.')
            note = message
        elif user_blocked:
            # no message: individual messages are only possible inside ESI form
            # no note: handled inside form template
            note = None
        elif self.community_maintenance['scheduled']:
            message = self.community_maintenance['text_scheduled']
        elif authenticated and not valid_community_login:
            note = (u'Aufgrund eines technischen Fehlers steht Ihnen die '
                    u'Kommentarfunktion kurzfristig nicht zur Verfügung. '
                    u'Bitte entschuldigen Sie diese Störung.')

        return {
            # For not authenticated users this means "show_login_prompt".
            'show_comment_form': (
                not self.community_maintenance['active'] and
                self.commenting_allowed and self.comments_loadable and
                ((not user_blocked and valid_community_login) or
                 not authenticated)),
            'note': note,
            'message': message,
            'user_blocked': user_blocked,
            'show_premoderation_warning_user': premoderation_user and (
                self.commenting_allowed and not user_blocked),
            'show_premoderation_warning_article': self.article_premoderate
        }

    @zeit.web.reify
    def comment_count(self):
        return self.community.get_comment_count(self.context.uniqueId)

    @zeit.web.reify
    def comment_area(self):
        result = {
            'show_comments': not self.community_maintenance['active'] and (
                self.comments_loadable and bool(self.comments)),
            'no_comments': (not self.comments and self.comments_loadable),
        }
        # XXX Do we really want all these variables under the same name or
        # should we split up access in the templates instead?
        result.update(self.comment_form)
        return result

    @zeit.web.reify
    def moderation_url(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        toggles = zeit.web.core.application.FEATURE_TOGGLES
        if not toggles.find('zoca_moderation_launch'):
            uuid = zeit.cms.content.interfaces.IUUID(
                self.context).shortened
            if not uuid:
                return None
            return u'{}/{}/thread/%cid%'.format(
                conf.get('community_admin_host').rstrip('/'), uuid)
        else:
            return u'{}/comment/edit/%cid%'.format(
                conf.get('community_profile_url').rstrip('/'))


class Content(zeit.web.core.paywall.CeleraOneMixin, CommentMixin, Base):

    """Base view class for content that a) provides ICommonMetadata and b) is a
    "single content" (e.g. article/gallery/video, but not centerpage).
    XXX We should introduce an interface for this.
    """

    @zeit.web.reify
    def basename(self):
        return os.path.basename(self.request.path.rstrip('/'))

    @zeit.web.reify
    def subtitle(self):
        return self.context.subtitle

    @zeit.web.reify
    def date_print_published(self):
        date = self.publish_info.date_print_published
        if date:
            return date.astimezone(self.timezone)

    @zeit.web.reify
    def show_date_format(self):
        if self.date_last_modified != self.date_first_released:
            return 'long'
        elif self.product_id in ('ZEI', 'ZMLB'):
            return 'short'
        return 'long'

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
        today = datetime.datetime.now(self.timezone).date()
        yesterday = (today - datetime.timedelta(days=1))

        if self.leadtime.start:
            # start = today
            if self.leadtime.start.date() == today:
                return True
            # start = yesterday and no end
            elif (self.leadtime.start.date() == yesterday and not
                  self.leadtime.end):
                return True
        if self.leadtime.end and self.leadtime.end.date() == today:
            # end = today
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
    def last_modified_label(self):
        if self.date_last_modified != self.date_first_released:
            return u'{} am {}'.format(
                self.last_modified_wording,
                zeit.web.core.template.format_date(
                    self.date_last_modified, 'long'))

    @zeit.web.reify
    def obfuscated_date(self):
        if self.last_modified_label:
            date = zeit.web.core.template.format_date(
                self.date_first_released, self.show_date_format)
            return base64.b64encode(date.encode('latin-1'))

    @zeit.web.reify
    def issue_format(self):
        return u' Nr.\u00A0{}/{}'

    @zeit.web.reify
    def last_modified_wording(self):
        if self.context.product and self.context.product.show == 'issue':
            return 'Editiert'
        return 'Aktualisiert'

    @zeit.web.reify
    def source_label(self):
        src_str = 'Quelle: '
        # freeform sources
        if self.context.copyrights:
            return src_str + self.context.copyrights
        # xml show option
        if self.context.product and self.context.product.show:
            label = self.context.product.label or self.context.product.title
            if self.context.product.show == 'issue' and self.context.volume:
                label += self.issue_format.format(self.context.volume,
                                                  self.context.year)
            elif self.context.product.show == 'source':
                label = src_str + label
            return label

    @zeit.web.reify
    def source_url(self):
        if self.context.deeplink_url:
            return self.context.deeplink_url
        elif self.context.product and self.context.product.show == 'link':
            return self.context.product.href

    @zeit.web.reify
    def obfuscated_source(self):
        if self.unobfuscated_source:
            return base64.b64encode(self.unobfuscated_source.encode('latin-1'))

    @zeit.web.reify
    def unobfuscated_source(self):
        if self.context.product and self.context.product.show == 'issue':
            if self.source_label and self.date_print_published:
                return u'{}, {}'.format(
                    self.source_label,
                    babel.dates.format_date(self.date_print_published,
                                            "d. MMMM yyyy", locale="de_De"))

    @zeit.web.reify
    def webtrekk(self):
        webtrekk = super(Content, self).webtrekk
        custom_parameter = webtrekk['customParameter']

        if self.nextread_ad:
            parsed = urlparse.urlparse(self.nextread_ad[0].url)
            custom_parameter['cp33'] = ''.join(parsed[1:3])

        return webtrekk

    @zeit.web.reify
    def ligatus(self):
        ressort_blacklisted = (self.ressort in LIGATUS_BLACKLIST) or (
            self.sub_ressort in LIGATUS_BLACKLIST)

        return (
            zeit.web.core.application.FEATURE_TOGGLES.find('ligatus') and
            self.advertising_enabled and not ressort_blacklisted and
            not getattr(self.context, 'hide_ligatus_recommendations', False))

    @zeit.web.reify
    def ligatus_special(self):
        ligatus_special_output = []

        ligatus_special_taglist = ['D17', 'D18']
        for keyword in self.context.keywords:
            if keyword.label in ligatus_special_taglist:
                ligatus_special_output.append(keyword.label)

        if self.serie:
            ligatus_special_output.append(self.serie)

        return ligatus_special_output

    @zeit.web.reify
    def contains_video(self):
        return False

    @zeit.web.reify
    def ligatus_do_not_index(self):
        if getattr(self.context, 'no_ligatus_indexing_allowed', False):
            return True
        if getattr(self, 'is_advertorial', None):
            return True
        # galleries or videos do not have pagination: so be defensive!
        if getattr(self, 'pagination', None):
            if getattr(self, 'is_all_pages_view', False):
                return True
            elif self.pagination.get('current') > 1:
                return True
        # actually we aim for comment pagination, but it is also good to
        # not trigger indexing with campaign params and stuff
        if self.request.query_string:
            return True
        return False

    @zeit.web.reify
    def nextread(self):
        return zeit.web.core.interfaces.INextread(self.context, [])

    @zeit.web.reify
    def nextread_ad(self):
        return zope.component.queryAdapter(
            self.context, zeit.web.core.interfaces.INextread,
            'advertisement', [])

    # XXX Does this really belong on this class?
    @zeit.web.reify('default_term')
    def comment_counts(self):
        return self.community.get_comment_counts(
            *[t.uniqueId for t in self.nextread])


@zeit.web.view_config(route_name='health_check')
def health_check(request):
    """ View callable to perform a health a check by checking,
        if the configured repository path exists.

        :type arg1: pyramid request object
        :return: Response indicating, if check was successful or not
        :rtype: pyramid.response.Response
    """

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    if not conf.get('health_check_with_fs', False):
        return pyramid.response.Response('OK', 200)

    path = urlparse.urlparse(
        zeit.web.core.application.maybe_convert_egg_url(
            conf.get(
                'vivi_zeit.connector_repository-path',
                'file:///var/cms/work/')))
    if not os.path.exists(getattr(path, 'path', '/var/cms/work/')):
        raise pyramid.httpexceptions.HTTPInternalServerError()

    return pyramid.response.Response('OK', 200)


class service_unavailable(object):  # NOQA

    def __init__(self, context, request):
        try:
            path = request.path
        except UnicodeDecodeError:
            # path_info is not exactly what request.path returns, but should be
            # close enough.
            path = request.environ.get('PATH_INFO').decode(
                request.url_encoding, 'replace')
        log.error(u'Error at {}'.format(path), exc_info=True)
        bugsnag.notify(context, severity='error', context=path)

    def __call__(self):
        body = 'Status 503: Dokument zurzeit nicht verfügbar.'
        return pyramid.response.Response(body, 503)


class FrameBuilder(zeit.web.core.paywall.CeleraOneMixin):

    inline_svg_icons = True

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        self.request.response.headers.add('Access-Control-Allow-Origin', '*')

    @zeit.web.reify
    def framebuilder_is_minimal(self):
        return 'minimal' in self.request.GET

    @zeit.web.reify
    def framebuilder_width(self):
        return self.request.GET.get('width', None)

    @zeit.web.reify
    def framebuilder_has_login(self):
        return 'login' in self.request.GET

    @zeit.web.reify
    def framebuilder_loginstatus_disabled(self):
        # This (GET param) is double-negative, so we can
        # remove everything as soon as we do not need the safety net any longer
        return 'loginstatus_disabled' in self.request.GET

    @zeit.web.reify
    def advertising_enabled(self):
        return self.banner_channel is not None

    @zeit.web.reify
    def banner_channel(self):
        return self.request.GET.get('banner_channel', None)

    @zeit.web.reify
    def ressort(self):
        return self.request.GET.get('ressort', '').lower()

    @zeit.web.reify
    def page_slice(self):
        requested_slice = self.request.GET.get('page_slice', None)
        if requested_slice:
            if requested_slice not in [
                    'html_head', 'upper_body', 'lower_body']:
                raise pyramid.httpexceptions.HTTPBadRequest(
                    title='Bad page_slice given',
                    explanation='''The page_slice parameter only accepts these
                        values: "html_head", "upper_body", "lower_body"''')
        return requested_slice

    @zeit.web.reify
    def desktop_only(self):
        return 'desktop_only' in self.request.GET

    @zeit.web.reify
    def framebuilder_requires_webtrekk(self):
        return 'webtrekk' in self.request.GET

    @zeit.web.reify
    def framebuilder_requires_ivw(self):
        return 'ivw' in self.request.GET

    @zeit.web.reify
    def framebuilder_requires_meetrics(self):
        return 'meetrics' in self.request.GET

    @zeit.web.reify
    def nav_show_ressorts(self):
        return 'hide_ressorts' not in self.request.GET

    @zeit.web.reify
    def nav_show_search(self):
        return 'hide_search' not in self.request.GET

    @zeit.web.reify
    def is_advertorial(self):
        return 'adlabel' in self.request.GET

    @zeit.web.reify
    def cap_title(self):
        return self.request.GET.get('adlabel') or 'Anzeige'

    @zeit.web.reify
    def adcontroller_values(self):
        if not self.banner_channel:
            return []

        adc_levels = self.banner_channel.split('/')
        handle = adc_levels[3] if len(adc_levels) > 3 else ''

        if handle != '' and not handle.endswith('_trsf'):
            handle = '{}_trsf'.format(handle)

        return [('$handle', handle),
                ('level2', adc_levels[0] if len(adc_levels) > 0 else ''),
                ('level3', adc_levels[1] if len(adc_levels) > 1 else ''),
                ('level4', adc_levels[2] if len(adc_levels) > 2 else ''),
                ('$autoSizeFrames', True),
                ('keywords', adc_levels[4] if len(adc_levels) > 4 else ''),
                ('tma', '')]


@pyramid.view.notfound_view_config()
def not_found(request):
    if request.path.startswith('/error/404'):  # Safetybelt
        log.warn('404 for /error/404, returning synthetic response instead')
        return pyramid.response.Response(
            'Status 404: Dokument nicht gefunden.', 404)
    host = request.headers.get('Host', 'www.zeit.de')
    www_host = host
    if not host.startswith('localhost') and not host.startswith('www'):
        parts = host.split('.')
        www_host = '.'.join(['www'] + parts[1:])
    return pyramid.response.Response(render_not_found_body(www_host), 404)


@DEFAULT_TERM_CACHE.cache_on_arguments(should_cache_fn=bool)
def render_not_found_body(hostname):
    subrequest = pyramid.request.Request.blank(
        '/error/404', headers={'Host': hostname})
    request = pyramid.threadlocal.get_current_request()
    response = request.invoke_subrequest(subrequest, use_tweens=True)
    if response.status_int not in (200, 404):
        return None
    return response.body


@zeit.web.view_config(context=pyramid.exceptions.URLDecodeError)
# Unfortunately, not everyone raises a specific error, so we need to catch
# the generic one, too. (See also <https://github.com/Pylons/webob/issues/115>)
@zeit.web.view_config(context=UnicodeDecodeError)
def invalid_unicode_in_request(request):
    body = 'Status 400: Invalid unicode data in request.'
    return pyramid.response.Response(body, 400)


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/login-state-footer.html',
    request_param='for=footer',
    http_cache=60)
def login_state_footer(request):
    return zeit.web.core.security.get_login_state(request)


@zeit.web.view_config(
    route_name='robots',
    host_restriction=False)
def robots_txt(request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    hostname = request.headers.get('host', 'www.zeit.de').lower()
    subdomain = hostname.split('.')[0]

    folder = conf.get('robots_txt_prefix')
    if zeit.cms.interfaces.ICMSContent(
            '%s/%s' % (folder, subdomain), None) is None:
        subdomain = 'www'

    prefix = urlparse.urlparse(folder).path
    subrequest = pyramid.request.Request.blank('%s/%s' % (prefix, subdomain))
    return request.invoke_subrequest(subrequest, use_tweens=True)
