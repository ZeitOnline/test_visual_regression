# -*- coding: utf-8 -*-
import datetime
import logging
import re

from pyramid.view import view_config, view_defaults
import lxml.etree
import pyramid.httpexceptions
import zope.component

import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces

from zeit.web.site.view_feed import (
    CONTENT_MAKER, ELEMENT_MAKER,
    create_public_url, last_published_semantic, format_iso8601_date)
import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view


log = logging.getLogger(__name__)


class Article(zeit.web.core.view.Content):

    advertising_enabled = True
    is_longform = False
    page_nr = 1

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.banner_on
        self.context.is_longform = self.is_longform
        self.context.current_year = datetime.date.today().year
        # throw 404 for 'komplettansicht' if there's just one article page
        if self.is_all_pages_view and len(self.pages) == 1:
            raise pyramid.httpexceptions.HTTPNotFound()

    @zeit.web.reify
    def template(self):
        return self.context.template or 'default'

    @zeit.web.reify
    def header_layout(self):
        return self.context.header_layout or 'default'

    @zeit.web.reify
    def pages(self):
        return zeit.web.core.interfaces.IPages(self.context)

    @zeit.web.reify
    def is_all_pages_view(self):
        return self.request.view_name == 'komplettansicht'

    @zeit.web.reify
    def current_page(self):
        return self.pages[0]

    @zeit.web.reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser

    @zeit.web.reify
    def pages_titles(self):
        titles = []
        for number in range(0, len(self.pages)):
            title = self.title
            if number > 0:
                title = self.pages[number].teaser
            titles.append(title)
        return titles

    def _pagetitle(self, suffix):
        try:
            title = zeit.seo.interfaces.ISEO(self.context).html_title
            assert title
        except (AssertionError, TypeError):
            if self.page_nr > 1 and self.current_page.teaser:
                title = ': '.join(
                    [t for t in (
                        getattr(self, 'supertitle'),
                        self.current_page.teaser) if t])
            else:
                title = ': '.join(
                    [t for t in (
                        self.supertitle, self.title) if t])
        if title and suffix:
            return u'{}{}'.format(title, self.pagetitle_suffix)
        if title:
            return title

        return self.seo_title_default

    @zeit.web.reify
    def pages_urls(self):
        urls = []
        for number in range(0, len(self.pages)):
            url = self.content_url
            if number > 0:
                url += '/seite-' + str(number + 1)
            urls.append(url)
        return urls

    @zeit.web.reify
    def next_page_url(self):
        if self.is_all_pages_view:
            return None
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index + 1] \
            if actual_index + 1 < len(self.pages) else None

    @zeit.web.reify
    def prev_page_url(self):
        actual_index = self.page_nr - 1
        return self.pages_urls[actual_index - 1] \
            if actual_index - 1 >= 0 else None

    @zeit.web.reify
    def pagination(self):
        current = self.page_nr
        total = len(self.pages)
        pager = zeit.web.core.template.calculate_pagination(current, total)

        return {
            'current': current,
            'total': total,
            'pager': pager,
            'next_page_title': self.next_title,
            'content_url': self.content_url,
            'pages_titles': self.pages_titles,
            'pages_urls': self.pages_urls,
            'next_page_url': self.next_page_url,
            'prev_page_url': self.prev_page_url
        }

    @zeit.web.reify
    def syndication_source(self):
        return self.source_url

    @zeit.web.reify
    def has_cardstack(self):
        return (self.context.xml.xpath('/article/body//cardstack') or
                self.context.xml.xpath('/article/head/header/cardstack'))

    @zeit.web.reify
    def cardstack_body(self):
        url = super(Article, self).cardstack_body
        params = dict(shareUrl=self.canonical_url)
        return zeit.web.core.utils.update_get_params(url, **params)

    @zeit.web.reify
    def header_elem(self):
        return zeit.web.core.interfaces.IFrontendBlock(
            zeit.content.article.edit.interfaces.IHeaderArea(
                self.context).module, None)

    @zeit.web.reify
    def resource_url(self):
        return self.request.resource_url(self.context).rstrip('/')

    @zeit.web.reify
    def authors(self):
        return zeit.web.core.article.convert_authors(
            self.context, self.is_longform)

    @zeit.web.reify
    def authors_list(self):
        if self.authors:
            return u';'.join([
                rt['name'] for rt in self.authors if rt.get('name')])
        return ''

    @zeit.web.reify
    def linkreach(self):
        reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
        return reach.get_buzz(self.context.uniqueId).get('social')

    @zeit.web.reify
    def tracking_type(self):
        return self.type

    @zeit.web.reify
    def text_length(self):
        return self.context.textLength

    @zeit.web.reify
    def news_source(self):
        """1:1 implementation of questionable xslt construct"""
        if (self.context.ressort == 'News' and
                self.context.product and self.context.product.id == 'News'):
            return 'dpa'
        elif self.context.product and self.context.product.id == 'SID':
            return 'Sport-Informations-Dienst'
        else:
            try:
                return self.context.copyrights.replace(
                    ',', ';').replace(' ', '')
            except(AttributeError):
                return ""

    @zeit.web.reify
    def is_breaking(self):
        try:
            return zeit.content.article.interfaces.IBreakingNews(
                self.context).is_breaking
        except:
            return False

    @zeit.web.reify
    def is_push_news(self):
        return self.context.push_news

    @zeit.web.reify
    def amp_url(self):
        path = '/'.join(self.request.traversed)
        return self.request.route_url('home') + 'amp/' + path

    @zeit.web.reify
    def is_amp(self):
        return self.context.is_amp

    @zeit.web.reify
    def advertorial_marker(self):
        try:
            return (
                self.context.advertisement_title,
                self.context.advertisement_text,
                self.cap_title)
        except AttributeError:
            return None

    @zeit.web.reify
    def pdf_link(self):
        server = 'http://pdf.zeit.de/'
        path = '/'.join(self.request.traversed)
        return server + path + '.pdf'

    @zeit.web.reify
    def print_link(self):
        url = self.content_url
        prefix = '/komplettansicht'

        try:
            if len(self.pages) == 1:
                prefix = ''
        except:
            pass

        path = prefix + '?print'
        return url + path

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Article, self).breadcrumbs
        # News
        if self.ressort == 'news':
            breadcrumbs.append(('News', 'http://xml.zeit.de/news/index'))
            self.breadcrumbs_by_title(breadcrumbs)
            return breadcrumbs
        # Archive article
        if self.product_id in ('ZEI', 'ZEAR'):
            breadcrumbs.append(
                ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'))
            # Beware, we have some pretty messy archive data...
            try:
                breadcrumbs.extend([
                    ("Jahrgang {}".format(self.context.year),
                        'http://xml.zeit.de/{}/index'.format(
                            self.context.year)),
                    ("Ausgabe: {0:02d}".format(self.context.volume),
                        'http://xml.zeit.de/{0}/{1:02d}/index'.format(
                            self.context.year, self.context.volume))])
                self.breadcrumbs_by_title(breadcrumbs)
                return breadcrumbs
            except ValueError:
                return self.breadcrumbs_by_title(breadcrumbs)
        # Ordinary articles
        self.breadcrumbs_by_navigation(breadcrumbs)
        page_teaser = self.current_page.teaser
        if len(page_teaser) > 0:
            breadcrumbs.extend([(page_teaser, self.context.uniqueId)])
        else:
            self.breadcrumbs_by_title(breadcrumbs)
        return breadcrumbs

    WEBTREKK_ASSETS = (
        'cardstack', 'inlinegallery', 'liveblog', 'quiz', 'raw', 'video')

    @zeit.web.reify
    def webtrekk_assets(self):
        assets = []

        block_type = zeit.web.core.template.block_type(self.header_elem)
        if block_type in self.WEBTREKK_ASSETS:
            assets.append('{}.header/seite-1'.format(block_type))

        p = 0
        for nr, page in enumerate(self.pages, start=1):
            for block in page:
                block_type = zeit.web.core.template.block_type(block)
                if block_type == 'paragraph':
                    p += 1
                if block_type in self.WEBTREKK_ASSETS:
                    assets.append('{}.{}/seite-{}'.format(block_type, p, nr))
        return assets


class AcceleratedMobilePageArticle(Article):

    @zeit.web.reify
    def meta_robots(self):
        return super(AcceleratedMobilePageArticle,
                     self).meta_robots.replace(',noarchive', '')

    @zeit.web.reify
    def webtrekk(self):
        webtrekk = super(AcceleratedMobilePageArticle, self).webtrekk

        webtrekk['customParameter'].update({
            'cp12': 'mobile.site',  # Seitenversion Endgerät
            'cp13': 'mobile',  # Breakpoint
            'cp25': 'amp'  # Plattform
        })

        return webtrekk


@view_config(route_name='amp',
             context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(lambda context, _: not context.is_amp,),
             request_method='GET')
def redirect_amp_disabled(context, request):
    url = request.url.replace('/amp/', '/', 1)
    raise pyramid.httpexceptions.HTTPFound(url)


@view_defaults(context=zeit.content.article.interfaces.IArticle)
@view_config(route_name='instantarticle')
@view_config(route_name='instantarticle-item',
             wrapper='instantarticle-item')
class InstantArticle(Article):

    def __call__(self):
        try:
            return pyramid.renderers.render_to_response(
                'templates/instantarticle/article.html',
                {'view': self}, request=self.request)
        except zeit.web.core.jinja.Interrupt, err:
            log.debug('Contained article block_type %s not implemented.' % (
                zeit.web.core.template.block_type(err.message)))
            return pyramid.response.Response(
                headerlist=[('X-Interrupt', 'true')])

    @zeit.web.reify
    def authors(self):
        return super(InstantArticle, self).authors or [{'name': 'ZEIT ONLINE'}]

    @zeit.web.reify
    def date_last_published(self):
        date = self.publish_info.date_last_published
        if date:
            return date.astimezone(self.timezone)

    @zeit.web.reify
    def fbia_first_ad_paragraph(self, words=100):
        """Returns tuple with page/block coordinates of first p where an
        fbia ad is possible. Take this Zuckerberg!"""
        for p, page in enumerate(self.pages):
            for b, block in enumerate(page.blocks):
                if isinstance(block, zeit.web.core.block.Paragraph):
                    words = words - len(
                        re.findall(r'\S+', block.model_block.text))
                    if words < 0:
                        return (p, b)
        return None


@view_config(context=zeit.content.article.interfaces.IArticle,
             name='instantarticle-item',
             renderer='string')
class InstantArticleItem(Article):

    def __call__(self):
        if not getattr(self.request, 'wrapped_response', None) or (
                'X-Interrupt', 'true') in (
                    self.request.wrapped_response.headerlist):
            return pyramid.response.Response(
                headerlist=[('X-Interrupt', 'true')])

        metadata = zeit.cms.content.interfaces.ICommonMetadata(self.context)

        title = u': '.join(t for t in (
            metadata.supertitle, metadata.title) if t)

        content_url = create_public_url(
            zeit.web.core.template.create_url(
                None, self.context, self.request))

        if getattr(self.context, 'authorships', None):
            authors = [getattr(author.target, 'display_name', None)
                       for author in self.context.authorships]
            authors = u', '.join(a for a in authors if a)
        else:
            authors = u''

        pub_date = format_iso8601_date(last_published_semantic(self.context))

        body = lxml.etree.CDATA(self.request.wrapped_response.text)

        E = ELEMENT_MAKER  # NOQA
        item = E.item(
            E.title(title),
            E.link(content_url),
            E.description(metadata.teaserText),
            E.category(metadata.sub_ressort or metadata.ressort),
            E.author(authors),
            E.pubDate(pub_date),
            E.guid(content_url, isPermaLink='false'),
            CONTENT_MAKER(body))

        return lxml.etree.tostring(item)


@view_config(context=zeit.content.article.interfaces.IArticle,
             route_name='fbia',
             renderer='templates/instantarticle/tracking.html')
class InstantArticleTracking(Article):

    @zeit.web.reify
    def webtrekk(self):
        webtrekk = super(InstantArticleTracking, self).webtrekk

        webtrekk['customParameter'].update({
            'cp25': 'instant article'  # Plattform
        })

        return webtrekk


class ArticlePage(Article):

    def __call__(self):
        self._validate_and_determine_page_nr()
        super(ArticlePage, self).__call__()
        return {}

    @zeit.web.reify
    def page_nr(self):
        return self._validate_and_determine_page_nr()

    def _validate_and_determine_page_nr(self):
        # see https://github.com/ZeitOnline/zeit.web/wiki/Artikel#seo
        try:
            spec = self.request.path_info.split('/')[-1][6:]
            number = int(re.sub('[^0-9]', '', spec))
        except (AssertionError, IndexError, ValueError):
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                self.resource_url)
        else:
            if len(str(number)) != len(spec):
                # Make sure /seite-007 is redirected to /seite-7
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    '%s/%s-%s' % (
                        self.resource_url, self.request.view_name, number))
            elif number > len(self.pages):
                raise pyramid.httpexceptions.HTTPNotFound()
            elif number == 1 or number == 0:
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    self.resource_url)
            return number

    @zeit.web.reify
    def current_page(self):
        return self.pages[self.page_nr - 1]

    @zeit.web.reify
    def next_title(self):
        if self.page_nr < len(self.pages):
            return self.pages[self.page_nr].teaser
