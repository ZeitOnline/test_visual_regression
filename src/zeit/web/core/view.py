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

from zeit.solr import query as lq
import zeit.cms.tagging.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.text.interfaces
import zeit.solr.interfaces

import zeit.web
import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.core.cache
import zeit.web.core.comments
import zeit.web.core.date
import zeit.web.core.template
import zeit.web.core.navigation
import zeit.web.core.paywall


SHORT_TERM_CACHE = zeit.web.core.cache.get_region('short_term')
log = logging.getLogger(__name__)


def known_content(resource):
    return (zeit.content.article.interfaces.IArticle.providedBy(resource) or
            zeit.content.gallery.interfaces.IGallery.providedBy(resource) or
            zeit.content.video.interfaces.IVideo.providedBy(resource))


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'


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


def redirect_on_cp2015_suffix(request):
    if request.path.endswith('.cp2015') and not len(request.path) == 7:
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(
            request.url)
        url = '{}://{}{}'.format(scheme, netloc, path[:-7])
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
        # Don't redirect for preview (since the workingcopy does not contain
        # the suffix-less version)
        if pyramid.settings.asbool(self.request.registry.settings.get(
                'redirect_from_cp2015', True)):
            redirect_on_cp2015_suffix(self.request)

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
    def is_advertorial(self):
        return is_advertorial(self.context, self.request)

    @zeit.web.reify
    def serie(self):
        if self.context.serie is None:
            return ''
        return self.context.serie.serienname

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

    def banner_toggles(self, name):
        return None

    @zeit.web.reify
    def adcontroller_handle(self):
        replacements = {
            'article': 'artikel',
            'author': 'centerpage',
            'centerpage': 'centerpage',
            'gallery': 'galerie',
            'quiz': 'quiz',
            'video': 'video_artikel'}
        if self.is_hp:
            return 'homepage'
        if self.is_advertorial:
            return '{}_{}'.format(
                'mcs' if 'mcs/' in self.banner_channel else 'adv',
                'index' if self.type == 'centerpage' else 'artikel')
        if self.type == 'centerpage' and (
                self.sub_ressort == '' or self.ressort == 'zeit-magazin'):
            return 'index'
        if self.type in replacements:
            return replacements[self.type]
        return 'centerpage'

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
        keywords = ','.join(self.adwords) if (
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
        return 'index,follow,noodp,noydir,noarchive'

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
        names = ('banner_channel', 'ressort', 'sub_ressort', 'type', 'paywall')
        return [(name, getattr(self, name, '')) for name in names]

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
    def ranked_tags(self):
        tags = []
        for keyword in self.context.keywords:
            if not keyword.label:
                continue
            elif not keyword.url_value:
                uuid = keyword.uniqueId.replace('tag://', '')
                keyword = zope.component.getUtility(
                    zeit.cms.tagging.interfaces.IWhitelist).get(uuid)
                if keyword is None:
                    continue
            tags.append(keyword)
        return tags

    @zeit.web.reify
    def meta_keywords(self):
        if self.ranked_tags:
            result = [x.label for x in self.ranked_tags]
        else:
            result = [self.ressort.title(), self.sub_ressort.title()]
        return [x for x in result if x]

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
    def iqd_mobile_settings(self):
        iqd_ids = zeit.web.core.banner.IQD_MOBILE_IDS_SOURCE.ids
        if self.is_hp:
            return getattr(iqd_ids['hp'], 'centerpage')
        try:
            return getattr(iqd_ids[self.sub_ressort], self.type,
                           getattr(iqd_ids[self.sub_ressort], 'default'))
        except KeyError:
            return {}

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
    def ad_delivery_type(self):
        return 'adcontroller'

    @zeit.web.reify
    def breaking_news(self):
        return zeit.web.core.block.BreakingNews()

    @zeit.web.reify
    def content_path(self):
        return u'/' + u'/'.join(self.request.traversed).replace('.cp2015', '')

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
        return self.date_last_published_semantic or self.date_first_released

    @zeit.web.reify
    def date_first_released(self):
        date = self.publish_info.date_first_released
        if date:
            return date.astimezone(self.timezone)

    @zeit.web.reify
    def date_last_published_semantic(self):
        modified = self.publish_info.date_last_published_semantic
        released = self.date_first_released
        # use 60s of tolerance before displaying a modification date
        # whould be unnecessary if date_last_published_semantic is never before
        # first_released and initially undefined or equal first_released
        # but it's not like that [ms]
        if (released is not None and modified is not None and
                modified - released > datetime.timedelta(seconds=60)):
            return modified.astimezone(self.timezone)

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
        # beware of None
        product_id = get_param('product_id')

        if getattr(self, 'pagination', None):
            if getattr(self, 'is_all_pages_view', False):
                page = 'all'
            else:
                page = self.pagination.get('current')
            pagination = '{}/{}'.format(page, self.pagination.get('total'))

        if getattr(self, 'is_push_news', False):
            push = 'wichtigenachrichten.push'
        elif getattr(self, 'is_breaking', False):
            push = 'eilmeldung.push'
        else:
            push = ''

        if getattr(self, 'framebuilder_requires_webtrekk', False):
            pagetype = 'centerpage.framebuilder'
        else:
            pagetype = self.detailed_content_type

        content_group = collections.OrderedDict([
            ('cg1', 'redaktion'),  # Zuordnung/Bereich
            ('cg2', get_param('tracking_type')),  # Kategorie
            ('cg3', get_param('ressort')),  # Ressort
            ('cg4', product_id),  # Online/Sourcetype
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
            ('cp8', product_id),  # Product-ID
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
            ('cp30', self.paywall or 'open')  # Paywall Schranke
        ])

        if zeit.web.core.template.toggles('access_status_webtrekk'):
            access = getattr(self.context, 'access', '')
            custom_parameter.update({'cp28': access})

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
        content_url = self.content_url.replace(u'http://', u'')
        return u'{}|{}'.format(self.webtrekk_identifier, content_url)

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
        if zeit.web.core.template.zplus_content(self.context) and (
                not self.paywall):
            code.append('paid')
        return '/'.join([x for x in code if x])

    @zeit.web.reify
    def share_buttons(self):
        if getattr(self.context, 'bigshare_buttons', None):
            return 'big'

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT ONLINE'

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitonline'

    @zeit.web.reify
    def paywall(self):
        return zeit.web.core.paywall.Paywall.status(self.request)


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

    @zeit.web.reify
    def comments(self):
        if not self.show_commentthread:
            return
        sort = self.request.params.get('sort', 'asc')
        try:
            page = int(self.request.params.get('page', 1))
        except ValueError:
            return
        cid = self.request.params.get('cid', None)
        return self.community.get_thread(
            self.context.uniqueId, sort=sort, page=page, cid=cid)

    def get_comment(self, cid):
        return self.community.get_comment(self.context.uniqueId, cid)

    @zeit.web.reify
    def commenting_allowed(self):
        return self.context.commentsAllowed and self.show_commentthread

    @zeit.web.reify
    def show_commentthread(self):
        return self.context.commentSectionEnable is not False

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
        premoderation = user.get('premoderation')
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
            'show_premoderation_warning': premoderation and (
                self.commenting_allowed and not user_blocked)
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
    def date_format(self):
        if self.product_id in ('ZEI', 'ZMLB'):
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
        if self.date_last_published_semantic:
            return u'{} am {}'.format(
                self.last_modified_wording,
                zeit.web.core.template.format_date(
                    self.date_last_published_semantic, 'long'))

    @zeit.web.reify
    def obfuscated_date(self):
        if self.last_modified_label:
            date = zeit.web.core.template.format_date(
                self.date_first_released, 'long')
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
            if self.source_label:
                label = self.source_label
                if self.date_print_published:
                    label += ', ' + babel.dates.format_date(
                        self.date_print_published,
                        "d. MMMM yyyy", locale="de_De")
                return label

    @zeit.web.reify('default_term')
    def lineage(self):
        if self.is_advertorial or not self.context.channels or (
                self.ressort == 'administratives'):
            return None

        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)

        def next(from_, to, sort):
            query = lq.and_(
                lq.datetime_range(
                    'date_first_released', from_, to),
                lq.bool_field(
                    'breaking_news', False),
                lq.field_raw(
                    'type', 'article'),
                lq.not_(
                    lq.field('uniqueId', self.context.uniqueId)),
                lq.not_(
                    lq.field('ressort', 'zeit-magazin')),
                lq.not_(
                    lq.field('ressort', 'Campus')),
                lq.text_range('channels', None, None),
                lq.field_raw(
                    'product_id', lq.or_(
                        'ZEDE', 'ZEI', 'ZECH', 'ZEC', 'ZEOE', 'ZES', 'ZTWI',
                        'ZTGS', 'ZTCS', 'CSRG', 'ZSF', 'KINZ')),
                lq.field(
                    'published', 'published'))
            with zeit.web.core.metrics.timer('lineage.solr.reponse_time'):
                return conn.search(query, sort='date_first_released ' + sort,
                                   fl='title supertitle uniqueId', rows=1).docs

        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_first_released

        default = [{
            'title': 'Startseite',
            'supertitle': '',
            'uniqueId': 'http://xml.zeit.de/index'}]
        predecessor = next(None, date, 'desc') or default
        successor = next(date, None, 'asc') or default
        if predecessor is default or successor is default:
            return zeit.web.dont_cache(predecessor + successor)

        return predecessor + successor

    @zeit.web.reify
    def webtrekk(self):
        webtrekk = super(Content, self).webtrekk
        style = 'share_buttons_{}'.format(self.share_buttons or 'small')

        webtrekk['customParameter'].update({
            'cp31': style  # share button style
        })

        return webtrekk

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

    def __call__(self):
        resp = super(FrameBuilder, self).__call__()
        # as long as we use the dirty ssl.zeit.de/* thing
        # we can only hack it into the asset pipeline
        # and hope for the best. We'll need https://www.zeit.de!
        if self.framebuilder_requires_ssl:
            try:
                self.request.asset_host = (
                    self.request.framebuilder_ssl_asset_host)
            except AttributeError:
                pass
        return resp

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
    def advertising_enabled(self):
        return self.banner_channel is not None and (
            self.framebuilder_requires_ssl is False)

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
    def framebuilder_requires_ssl(self):
        return 'useSSL' in self.request.GET

    @zeit.web.reify
    def adcontroller_values(self):
        if not self.banner_channel:
            return []

        adc_levels = self.banner_channel.split('/')

        return [('$handle', adc_levels[3] if len(adc_levels) > 3 else ''),
                ('level2', adc_levels[0] if len(adc_levels) > 0 else ''),
                ('level3', adc_levels[1] if len(adc_levels) > 1 else ''),
                ('level4', adc_levels[2] if len(adc_levels) > 2 else ''),
                ('$autoSizeFrames', True),
                ('keywords', adc_levels[4] if len(adc_levels) > 4 else ''),
                ('tma', '')]


@pyramid.view.notfound_view_config()
def not_found(request):
    body = 'Status 404: Dokument nicht gefunden.'
    return pyramid.response.Response(
        body, 404,
        [('X-Render-With', 'default'),
         ('Content-Type', 'text/plain; charset=utf-8')])


@zeit.web.view_config(context=pyramid.exceptions.URLDecodeError)
# Unfortunately, not everyone raises a specific error, so we need to catch
# the generic one, too. (See also <https://github.com/Pylons/webob/issues/115>)
@zeit.web.view_config(context=UnicodeDecodeError)
def invalid_unicode_in_request(request):
    body = 'Status 400: Invalid unicode data in request.'
    return pyramid.response.Response(body, 400)


def surrender(context, request):
    return pyramid.response.Response(
        'OK', 303, headerlist=[('X-Render-With', 'default')])


@zeit.web.view_config(route_name='blacklist')
def blacklist(context, request):
    return pyramid.httpexceptions.HTTPNotImplemented(
        headers=[('X-Render-With', 'default'),
                 ('Content-Type', 'text/plain; charset=utf-8')])


@zeit.web.view_config(
    route_name='json_delta_time',
    renderer='json')
def json_delta_time(request):
    unique_id = request.GET.get('unique_id', None)
    date = request.GET.get('date', None)
    base_date = request.GET.get('base_date', None)
    parsed_base_date = zeit.web.core.date.parse_date(base_date)
    if unique_id is not None:
        return json_delta_time_from_unique_id(
            request, unique_id, parsed_base_date)
    elif date is not None:
        return json_delta_time_from_date(date, parsed_base_date)
    else:
        return pyramid.response.Response(
            'Missing parameter: unique_id or date', 412)


def json_delta_time_from_date(date, parsed_base_date):
    parsed_date = zeit.web.core.date.parse_date(date)
    if parsed_date is None:
        return pyramid.response.Response(
            'Invalid parameter: date', 412)
    dt = zeit.web.core.date.DeltaTime(parsed_date, parsed_base_date)
    return {'delta_time': {'time': dt.get_time_since_modification()}}


def json_delta_time_from_unique_id(request, unique_id, parsed_base_date):
    try:
        content = zeit.cms.interfaces.ICMSContent(unique_id)
        assert zeit.content.cp.interfaces.ICenterPage.providedBy(content)
    except (TypeError, AssertionError):
        return pyramid.response.Response('Invalid resource', 400)
    delta_time = {}
    for article in zeit.web.site.view_centerpage.Centerpage(content, request):
        time = zeit.web.core.date.get_delta_time_from_article(
            article, base_date=parsed_base_date)
        if time:
            delta_time[article.uniqueId] = time
    return {'delta_time': delta_time}


@zeit.web.view_config(
    route_name='json_comment_count',
    renderer='json')
def json_comment_count(request):
    try:
        unique_id = request.GET.get('unique_id', None)
    except UnicodeDecodeError:
        unique_id = None
    if unique_id is None:
        return pyramid.response.Response(
            'Missing value for parameter: unique_id', 412)

    try:
        context = zeit.cms.interfaces.ICMSContent(unique_id)
    except TypeError:
        return pyramid.response.Response(
            'Invalid value for parameter: unique_id', 412)

    if zeit.content.cp.interfaces.ICenterPage.providedBy(context):
        articles = list(
            zeit.web.site.view_centerpage.Centerpage(context, request))
    else:
        article = zeit.content.article.interfaces.IArticle(context, None)
        articles = [article] if article is not None else []

    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    counts = community.get_comment_counts(*[a.uniqueId for a in articles])
    comment_count = {}

    for article in articles:
        count = counts.get(article.uniqueId, 0)
        comment_count[article.uniqueId] = '%s Kommentar%s' % (
            count == 0 and 'Keine' or count, count != '1' and 'e' or '')

    return {'comment_count': comment_count}


@zeit.web.view_config(
    context=zeit.content.text.interfaces.IText,
    renderer='string')
def view_textcontent(context, request):
    return context.text


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/login-state-footer.html',
    request_param='for=footer',
    http_cache=60)
def login_state_footer(request):
    return zeit.web.core.security.get_login_state(request)
