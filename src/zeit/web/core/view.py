# -*- coding: utf-8 -*-
import base64
import datetime
import logging
import lxml.etree
import re

import babel.dates
import bugsnag
import pyramid.response
import pyramid.view
import werkzeug.http

import zeit.cms.workflow.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.content.text.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.date

import zope.component

log = logging.getLogger(__name__)


def known_content(resource):
    return (zeit.content.article.interfaces.IArticle.providedBy(resource) or
            zeit.content.gallery.interfaces.IGallery.providedBy(resource) or
            zeit.content.video.interfaces.IVideo.providedBy(resource))


class Base(object):
    """Base class for all views."""

    seo_title_default = u''
    pagetitle_suffix = u''

    def __call__(self):
        # to avoid circular imports
        import zeit.web.site.view_feed

        # XXX: Since we do not have a configuration based on containments
        # for our views, this is necessary to control, that only explicitly
        # configured views, will render an RSS feed on newsfeed.zeit.de
        # host header (RD, 09-2015)
        if self.request.headers.get('host') == 'newsfeed.zeit.de' and not (
                issubclass(type(self), zeit.web.site.view_feed.Base)):
            raise pyramid.httpexceptions.HTTPNotFound()

        time = zeit.web.core.cache.ICachingTime(self.context)
        self.request.response.cache_expires(time)
        self._set_response_headers()
        return {}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @zeit.web.reify
    def vgwort_url(self):
        token = zeit.vgwort.interfaces.IToken(self.context).public_token
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if token and conf.get('vgwort_url'):
            return '{}/{}'.format(conf.get('vgwort_url'), token)

    @zeit.web.reify
    def enable_third_party_modules(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('enable_third_party_modules', True)

    @zeit.web.reify
    def enable_iqd(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('enable_iqd', True)

    @zeit.web.reify
    def enable_tracking(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('enable_tracking', True)

    def _set_response_headers(self):
        # ZMO Version header
        try:
            self.request.response.headers.add(
                'X-Version', self.request.registry.settings.version)
        except AttributeError:
            pass

        # C1 headers
        #
        # The following rules scream for inconsistency, but have already been
        # defined for tracking services long ago. :-(
        # Therefore they are just copied as is from the XSLT backend,
        # managing HTTP headers until launch.
        # (e.g. uppercase ressort vs lowercase sub ressort)

        # Additional predefined doc type values
        c1_add_doc_types = {
            'video': 'Video',
            'article': 'Artikel',
            'gallery': 'Bildergalerie'}

        # Additional predefined section (a.k.a. channel) values
        c1_add_sections = {
            'campus': 'Studium',
            'homepage': 'Homepage',
        }

        token = re.compile(r'[^ %s]' % ''.join(werkzeug.http._token_chars))

        c1_track_headers = {
            'C1-Track-Origin': lambda: 'web',
            'C1-Track-Service-ID': lambda: 'zon',
            'C1-Track-Doc-Type': lambda: c1_add_doc_types.get(
                self.type, 'Centerpage'),
            'C1-Track-Content-ID': lambda: '/' + '/'.join(
                self.request.traversed),
            'C1-Track-CMS-ID': lambda: zeit.cms.content.interfaces.IUUID(
                self.context).id,
            'C1-Track-Channel': lambda: c1_add_sections.get(
                self.context.ressort, self.context.ressort),
            'C1-Track-Sub-Channel': lambda: self.context.sub_ressort,
            'C1-Track-Heading': lambda: token.sub('', self.context.title),
            'C1-Track-Kicker': lambda: token.sub('', self.context.supertitle)
        }

        for th_name in c1_track_headers:
            try:
                track_header = c1_track_headers[th_name]()
            except (AttributeError, TypeError):
                continue
            if track_header is None:
                continue
            self.request.response.headers.add(
                th_name,
                track_header.encode('utf-8').strip())

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
    def serie(self):
        if self.context.serie is None:
            return ''
        return self.context.serie.serienname

    @zeit.web.reify
    def banner_channel(self):
        # manually banner_id rules first
        if self.context.banner_id is not None:
            return u'{}/{}'.format(self.context.banner_id, self.banner_type)
        # second rule: angebote are mapped with two levels
        if self.ressort == 'angebote':
            _serie = self.serie.replace(' ', '_')
            return u'{}/{}/{}'.format(self.ressort, _serie, self.banner_type)
        # third: do the mapping
        mappings = zeit.web.core.banner.banner_id_mappings
        for mapping in mappings:
            if getattr(self, mapping['target'], None) == mapping['value']:
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
        else:
            return 'index' if self.type == 'centerpage' and (
                self.sub_ressort == '' or self.ressort ==
                'zeit-magazin') else replacements[self.type]

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore."""
        levels = self.banner_channel.split('/')
        # remove type from level3
        levels[1] = '' if levels[1] == self.type else levels[1]
        return [('$handle', self.adcontroller_handle),
                ('level2', "".join(re.findall(r"[A-Za-z0-9_]*", levels[0]))),
                ('level3', "".join(re.findall(r"[A-Za-z0-9_]*", levels[1]))),
                ('level4', ''),
                ('$autoSizeFrames', True),
                ('keywords', ','.join(self.adwords)),
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
            return zeit.web.core.banner.banner_list[tile - 1]
        except IndexError:
            return

    @zeit.web.reify
    def canonical_url(self):
        """ Set own url as default canonical. Overwrite for special
            cases and page types"""
        return u"{}{}".format(self.request.host_url, self.request.path_info)

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
    def navigation_footer_publisher(self):
        return zeit.web.core.navigation.navigation_footer_publisher

    @zeit.web.reify
    def navigation_footer_links(self):
        return zeit.web.core.navigation.navigation_footer_links

    @zeit.web.reify
    def title(self):
        return self.context.title.strip()

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle

    @zeit.web.reify
    def pagetitle(self):
        try:
            title = zeit.seo.interfaces.ISEO(self.context).html_title
            assert title
        except (AssertionError, TypeError):
            title = ': '.join([t for t in (self.supertitle, self.title) if t])
        if title:
            return title + (u'' if self.is_hp else self.pagetitle_suffix)
        return self.seo_title_default

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
        return sorted([t for t in self.context.keywords if t.label],
                      key=lambda t: not t.url_value)

    @zeit.web.reify
    def ranked_tags_list(self):
        if self.ranked_tags:
            return ';'.join([rt.label for rt in self.ranked_tags])
        else:
            default_tags = [self.context.ressort, self.context.sub_ressort]
            return ';'.join([dt for dt in default_tags if dt])

    @zeit.web.reify
    def is_hp(self):
        try:
            return self.request.path == ('/{}'.format(
                self.request.registry.settings.hp))
        except AttributeError:
            return False

    @zeit.web.reify
    def is_wrapped(self):
        try:
            return ('app-content.zeit.de' in self.request.host_url) or (
                'app-content.staging.zeit.de' in self.request.host_url) or (
                self.is_dev_environment and (
                    'app-content' in self.request.query_string))
        except TypeError:
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
    def content_url(self):
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + path

    @zeit.web.reify
    def og_url(self):
        # for og url, hide cp2015 ending
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + path.replace(
            'index.cp2015', 'index')

    @zeit.web.reify
    def is_dev_environment(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('dev_environment', '')

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
        date = self.publish_info.date_last_published_semantic
        if (self.date_first_released is not None and date is not None and
                date > self.date_first_released):
            return date.astimezone(self.timezone)

    @zeit.web.reify
    def has_cardstack(self):
        return False


class Content(Base):

    is_longform = False

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
    def comments(self):
        if not self.show_commentthread:
            return

        sort = self.request.params.get('sort', 'asc')
        page = self.request.params.get('page', 1)
        cid = self.request.params.get('cid', None)
        return zeit.web.core.comments.get_thread(
            self.context.uniqueId,
            sort=sort,
            page=page,
            cid=cid)

    @zeit.web.reify
    def obfuscated_date(self):
        date = ''
        format = 'd. MMMM yyyy, H:mm \'Uhr\''
        first_released = babel.dates.format_datetime(
            self.date_first_released, format, locale='de_De')
        if self.context.product and self.context.product.show == 'issue':
            date = u'ver\u00F6ffentlicht am '
        date += first_released
        if self.date_last_published_semantic:
            date = u'{} ({} am {})'.format(
                date,
                self.last_modified_wording,
                babel.dates.format_datetime(
                    self.date_last_published_semantic, format, locale='de_De'))
        if date is not first_released:
            return base64.b64encode(date.encode('latin-1'))

    @zeit.web.reify
    def issue_format(self):
        return u' Nr.\u00A0{}/{}'

    @zeit.web.reify
    def last_modified_wording(self):
        if self.context.product and self.context.product.show == 'issue':
            return 'Editiert'
        return 'Zuletzt aktualisiert'

    @zeit.web.reify
    def source_label(self):
        if self.context.product and self.context.product.show:
            label = self.context.product.label or self.context.product.title
            if self.context.product.show == 'issue' and self.context.volume:
                label += self.issue_format.format(self.context.volume,
                                                  self.context.year)
            return label

    @zeit.web.reify
    def source_url(self):
        if self.context.deeplink_url:
            return self.context.deeplink_url
        elif self.context.product and self.context.product.show == 'link':
            return self.context.product.href

    @zeit.web.reify
    def obfuscated_source(self):
        if self.context.product and self.context.product.show == 'issue':
            if self.source_label:
                label = self.source_label
                if self.date_print_published:
                    label += ', ' + babel.dates.format_date(
                        self.date_print_published,
                        "d. MMMM yyyy", locale="de_De")
                return base64.b64encode(label.encode('latin-1'))

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
    def comment_counts(self):
        if self.nextread:
            return zeit.web.core.comments.get_counts(
                *[t.uniqueId for t in self.nextread])


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


# For some reason we are not able to register ICMSContent on this.
# We have to register this on every content-view.
@pyramid.view.view_config(context=zeit.content.cp.interfaces.ICenterPage)
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.gallery.interfaces.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
def surrender(context, request):
    return pyramid.response.Response(
        'OK', 200, headerlist=[('X-Render-With', 'default')])


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


@pyramid.view.view_config(
    route_name='toggle_third_party_modules',
    renderer='json',
    custom_predicates=(zeit.web.core.is_admin,))
def toggle_third_party_modules(request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['enable_third_party_modules'] = not conf['enable_third_party_modules']
    return conf


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
    except TypeError:
        return pyramid.response.Response('Invalid resource', 500)
    delta_time = {}
    for article in zeit.web.site.view_centerpage.Centerpage(content, request):
        time = zeit.web.core.date.get_delta_time_from_article(
            article, base_date=parsed_base_date)
        if time:
            delta_time[article.uniqueId] = time
    return {'delta_time': delta_time}


@pyramid.view.view_config(route_name='json_comment_count', renderer='json')
def json_comment_count(request):
    unique_id = request.GET.get('unique_id', None)
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
        articles = [zeit.content.article.interfaces.IArticle(context)]

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
