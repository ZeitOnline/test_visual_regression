# -*- coding: utf-8 -*-
import base64
import datetime
import logging
import lxml.etree
import os.path
import urlparse
import re

import babel.dates
import bugsnag
import pyramid.response
import pyramid.settings
import pyramid.view
import werkzeug.http
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
import zeit.web.core.comments
import zeit.web.core.date
import zeit.web.core.template
import zeit.web.core.navigation


log = logging.getLogger(__name__)


def known_content(resource):
    return (zeit.content.article.interfaces.IArticle.providedBy(resource) or
            zeit.content.gallery.interfaces.IGallery.providedBy(resource) or
            zeit.content.video.interfaces.IVideo.providedBy(resource))


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'


def is_paginated(context, request):
    try:
        return int(request.GET['p']) > 1
    except (KeyError, ValueError):
        return False


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


class Base(object):
    """Base class for all views."""

    seo_title_default = u''
    pagetitle_suffix = u''
    inline_svg_icons = False

    def __call__(self):
        # to avoid circular imports
        import zeit.web.site.view_feed

        # XXX: Since we do not have a configuration based on containments
        # for our views, this is necessary to control, that only explicitly
        # configured views, will render an RSS feed on newsfeed.zeit.de
        # host header (RD, 2015-09)
        host = self.request.headers.get('host', '')
        if re.match('newsfeed(\.staging)?\.zeit\.de', host) and not (
                issubclass(type(self), zeit.web.site.view_feed.Base)):
            raise pyramid.httpexceptions.HTTPNotFound()

        redirect_on_trailing_slash(self.request)
        # Don't redirect for preview (since the workingcopy does not contain
        # the suffix-less version)
        if pyramid.settings.asbool(self.request.registry.settings.get(
                'redirect_from_cp2015', True)):
            redirect_on_cp2015_suffix(self.request)
        time = zeit.web.core.interfaces.ICachingTime(self.context)

        # Make sure comments are loaded
        if hasattr(self, 'comments'):
            self.comments

        if not self.comments_loadable:
            time = 5
        self.request.response.cache_expires(time)

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
        self.comments_loadable = True

    @zeit.web.reify
    def vgwort_url(self):
        token = zeit.vgwort.interfaces.IToken(self.context).public_token
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if token and conf.get('vgwort_url'):
            return '{}/{}'.format(conf.get('vgwort_url'), token)

    @zeit.web.reify
    def third_party_modules_is_enabled(self):
        return zeit.web.core.application.FEATURE_TOGGLES.find(
            'third_party_modules')

    @zeit.web.reify
    def iqd_is_enabled(self):
        return zeit.web.core.application.FEATURE_TOGGLES.find(
            'iqd')

    @zeit.web.reify
    def tracking_is_enabled(self):
        return zeit.web.core.application.FEATURE_TOGGLES.find(
            'tracking')

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
            return ''
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
        # the famous 'entdecken/reisen' case, limited until 01/2016
        # return for all ressort 'entdecken' old code 'reisen'
        # there's always a first and a half rule
        if self.ressort == 'entdecken':
            return u'reisen/{}'.format(self.banner_type)
        # second rule: angebote are mapped with two levels
        if self.ressort == 'angebote':
            adv_title = self.context.advertisement_title or self.ressort
            return u'{}/{}/{}'.format(
                'adv',
                "".join(re.findall(r"[A-Za-z0-9_]*", adv_title)).lower(),
                self.banner_type)
        # third: do the mapping
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
        # subressort?
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
    def banner_on(self):
        # respect the global advertising switch
        if self.advertising_enabled is False or self.context.banner is False:
            return False
        # deliver banner if no banner is defined in xml
        if self.context.banner is None or self.context.banner is True:
            return True

    def banner_toggles(self, name):
        return None

    @zeit.web.reify
    def adcontroller_handle(self):
        replacements = {
            'article': 'artikel',
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
        return 'index' if self.type == 'centerpage' and (
            self.sub_ressort == '' or self.ressort ==
            'zeit-magazin') else replacements[self.type]

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
    def seo_robot_override(self):
        try:
            return zeit.seo.interfaces.ISEO(self.context).meta_robots
        except (AttributeError, TypeError):
            pass

    @zeit.web.reify
    def meta_robots(self):
        return self.seo_robot_override or 'index,follow,noodp,noydir,noarchive'

    @zeit.web.reify
    def adwords(self):
        keywords = ['zeitonline']
        # TODO: End discrepancy between testing and live ressorts!
        if self.ressort in ['zeit-magazin', 'lebensart']:
            keywords.append('zeitmz')
        return keywords

    def banner(self, tile):
        try:
            return list(zeit.web.core.banner.BANNER_SOURCE)[tile - 1]
        except IndexError:
            return

    @zeit.web.reify
    def canonical_url(self):
        """ Set own url as default canonical. Overwrite for special
            cases and page types"""
        return u"{}{}".format(
            self.request.route_url('home').rstrip('/'), self.request.path_info)

    @zeit.web.reify
    def js_vars(self):
        names = ('banner_channel', 'ressort', 'sub_ressort', 'type')
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
                    zeit.cms.tagging.interfaces.IWhitelist).get(uuid, None)
                if not keyword:
                    continue
            tags.append(keyword)
        return tags

    @zeit.web.reify
    def meta_keywords(self):
        if self.ranked_tags:
            result = [x.label for x in self.ranked_tags]
        else:
            result = [self.context.ressort, self.context.sub_ressort]
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
                conf.get('dev_environment') and
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
        return self.content_url  # XXX What's the point of this alias? (ND)

    @zeit.web.reify
    def sharing_image(self):
        return zeit.web.core.interfaces.ISharingImage(self.context, None)

    @zeit.web.reify
    def article_lineage_is_enabled(self):
        return zeit.web.core.application.FEATURE_TOGGLES.find(
            'article_lineage')

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


class CeleraOneMixin(object):

    def __call__(self):
        resp = super(CeleraOneMixin, self).__call__()
        self.request.response.headers.update(self.c1_header)
        return resp

    @zeit.web.reify
    def _c1_channel(self):
        if getattr(self.context, 'ressort', None) is not None:
            return self.context.ressort.lower()

    @zeit.web.reify
    def _c1_sub_channel(self):
        if getattr(self.context, 'sub_ressort', None) is not None:
            return self.context.sub_ressort.lower()

    @zeit.web.reify
    def _c1_cms_id(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.context, None)
        return getattr(uuid, 'id', None)

    @zeit.web.reify
    def _c1_doc_type(self):
        import zeit.web.site.view

        if self.type == 'gallery':
            return 'bildergalerie'
        elif isinstance(self, zeit.web.site.view.FrameBuilder):
            return 'arena'
        else:
            return self.type

    @classmethod
    def _headersafe(cls, string):
        pattern = r'[^ %s]' % ''.join(werkzeug.http._token_chars)
        return re.sub(pattern, '', string.encode('utf-8', 'ignore'))

    def _get_c1_heading(self, prep=unicode):
        if getattr(self.context, 'title', None) is not None:
            return prep(self.context.title.strip())

    def _get_c1_kicker(self, prep=unicode):
        if getattr(self.context, 'supertitle', None) is not None:
            return prep(self.context.supertitle.strip())

    @zeit.web.reify
    def c1_prefix(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('c1_prefix')

    @zeit.web.reify
    def c1_client(self):
        return [(k, u'"{}"'.format(v)) for k, v in {
            'set_channel': self._c1_channel,
            'set_sub_channel': self._c1_sub_channel,
            'set_cms_id': self._c1_cms_id,
            'set_content_id': self.content_path,
            'set_doc_type': self._c1_doc_type,
            'set_heading': self._get_c1_heading(),
            'set_kicker': self._get_c1_kicker(),
            'set_service_id': 'zon'
        }.items() if v is not None] + [
            ('set_origin', 'window.Zeit.getCeleraOneOrigin()')]

    @zeit.web.reify
    def c1_header(self):
        return [(k, v.encode('utf-8', 'ignore')) for k, v in {
            'C1-Track-Channel': self._c1_channel,
            'C1-Track-Sub-Channel': self._c1_sub_channel,
            'C1-Track-CMS-ID': self._c1_cms_id,
            'C1-Track-Content-ID': self.content_path,
            'C1-Track-Doc-Type': self._c1_doc_type,
            'C1-Track-Heading': self._get_c1_heading(self._headersafe),
            'C1-Track-Kicker': self._get_c1_kicker(self._headersafe),
            'C1-Track-Service-ID': 'zon'
        }.items() if v is not None]


class Content(CeleraOneMixin, Base):

    is_longform = False

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
        if self.context.product and self.context.product.id in ('ZEI', 'ZMLB'):
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
    def community_maintenance(self):
        return zeit.web.core.comments.community_maintenance()

    @zeit.web.reify
    def comments(self):
        if not self.show_commentthread:
            return

        sort = self.request.params.get('sort', 'asc')
        page = self.request.params.get('page', 1)
        cid = self.request.params.get('cid', None)
        try:
            return zeit.web.core.comments.get_thread(
                self.context.uniqueId,
                sort=sort,
                page=page,
                cid=cid)
        except zeit.web.core.comments.ThreadNotLoadable:
            self.comments_loadable = False
            return

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
            released = zeit.web.core.template.format_date(
                self.date_first_released, 'long')
            date = (u'{} <span class="metadata__seperator">'
                    ' / </span> {} ').format(
                        released,
                        self.last_modified_label)
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
    def comments_allowed(self):
        return self.context.commentsAllowed and self.show_commentthread

    @zeit.web.reify
    def show_commentthread(self):
        return self.context.commentSectionEnable is not False

    @zeit.web.reify
    def nextread(self):
        return zeit.web.core.interfaces.INextread(self.context)

    @zeit.web.reify
    def nextread_ad(self):
        return zope.component.getAdapter(
            self.context, zeit.web.core.interfaces.INextread,
            name="advertisement")

    @zeit.web.reify('default_term')
    def comment_counts(self):
        if self.nextread:
            return zeit.web.core.comments.get_counts(
                [t.uniqueId for t in self.nextread])

    @zeit.web.reify
    def comment_area(self):
        user_blocked = False
        premoderation = False
        uid = 0
        valid_community_login = True
        self.request.authenticated_userid

        if self.request.session.get('user'):
            user_blocked = self.request.session['user'].get('blocked')
            premoderation = self.request.session['user'].get('premoderation')
            uid = self.request.session['user'].get('uid')
            valid_community_login = True if uid and uid != '0' else False

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
        elif not self.comments_allowed:
            message = (u'Der Kommentarbereich dieses Artikels ist geschlossen.'
                       u' Wir bitten um Ihr Verständnis.')
            note = message
        elif user_blocked:
            # no message: individual messages are only possible inside ESI form
            # no note: handled inside form template
            note = None
        elif self.community_maintenance['scheduled']:
            message = self.community_maintenance['text_scheduled']

        if not valid_community_login:
            note = (u'Aufgrund eines technischen Fehlers steht Ihnen die '
                    u'Kommentarfunktion kurzfristig nicht zur Verfügung. '
                    u'Bitte entschuldigen Sie diese Störung.')

        return {
            'show': (self.comments_allowed or bool(self.comments)),
            'show_comment_form': not self.community_maintenance['active'] and (
                self.comments_allowed) and self.comments_loadable and (
                    not user_blocked) and valid_community_login,
            'show_comments': not self.community_maintenance['active'] and (
                self.comments_loadable and bool(self.comments)),
            'no_comments': (not self.comments and self.comments_loadable),
            'note': note,
            'message': message,
            'user_blocked': user_blocked,
            'show_premoderation_warning': premoderation and (
                self.comments_allowed and not user_blocked)
        }


@pyramid.view.view_config(route_name='health_check')
def health_check(request):
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


@pyramid.view.notfound_view_config()
def not_found(request):
    body = 'Status 404: Dokument nicht gefunden.'
    return pyramid.response.Response(body, 404, [('X-Render-With', 'default')])


@pyramid.view.view_config(context=pyramid.exceptions.URLDecodeError)
# Unfortunately, not everyone raises a specific error, so we need to catch
# the generic one, too. (See also <https://github.com/Pylons/webob/issues/115>)
@pyramid.view.view_config(context=UnicodeDecodeError)
def invalid_unicode_in_request(request):
    body = 'Status 400: Invalid unicode data in request.'
    return pyramid.response.Response(body, 400)


# For some reason we are not able to register ICMSContent on this.
# We have to register this on every content-view.
@pyramid.view.view_config(context=zeit.content.cp.interfaces.ICenterPage)
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.gallery.interfaces.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
@pyramid.view.view_config(route_name='schlagworte_index')
def surrender(context, request):
    return pyramid.response.Response(
        'OK', 303, headerlist=[('X-Render-With', 'default')])


@pyramid.view.view_config(route_name='blacklist')
def blacklist(context, request):
    return pyramid.httpexceptions.HTTPNotImplemented(
        headers=[('X-Render-With', 'default')])


@pyramid.view.view_config(route_name='json_delta_time', renderer='json')
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


@pyramid.view.view_config(route_name='json_comment_count', renderer='json')
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

    counts = zeit.web.core.comments.get_counts(*[a.uniqueId for a in articles])
    comment_count = {}

    for article in articles:
        count = counts.get(article.uniqueId, 0)
        comment_count[article.uniqueId] = '%s Kommentar%s' % (
            count == 0 and 'Keine' or count, count != '1' and 'e' or '')

    return {'comment_count': comment_count}


@pyramid.view.view_config(
    context=zeit.content.text.interfaces.IText,
    renderer='string')
def view_textcontent(context, request):
    return context.text


@pyramid.view.view_config(
    context=zeit.cms.content.interfaces.IXMLContent,
    route_name='xml',
    custom_predicates=(zeit.web.core.is_admin,))
def view_xml(context, request):
    xml = context.xml
    filter_xslt = lxml.etree.XML("""
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
            <xsl:template match="*|@*|text()">
                <xsl:copy>
                    <xsl:apply-templates select="*|@*|text()" />
                </xsl:copy>
            </xsl:template>
            <xsl:template match="cluster">
                <region>
                    <xsl:apply-templates select="*|@*|text()" />
                </region>
            </xsl:template>
            <xsl:template match="region">
                <area>
                    <xsl:apply-templates select="*|@*|text()" />
                </area>
            </xsl:template>
            <xsl:template match="container">
                <module>
                    <xsl:apply-templates select="*|@*|text()" />
                </module>
            </xsl:template>
        </xsl:stylesheet>""")
    try:
        transform = lxml.etree.XSLT(filter_xslt)
        return pyramid.response.Response(
            str(transform(xml)),
            content_type='text/xml')
    except TypeError:
        return
