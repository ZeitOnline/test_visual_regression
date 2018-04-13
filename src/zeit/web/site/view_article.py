# -*- coding: utf-8 -*-
import datetime
import logging

import babel.dates
import zope.component

from zeit.solr import query as lq
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.retresco.interfaces
import zeit.solr.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.metrics
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_article
import zeit.web.site.view


log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    vertical='zon')
@zeit.web.view_config(
    renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/article_advertorial.html')
@zeit.web.view_config(
    context=zeit.content.article.interfaces.IErrorPage,
    renderer='templates/article_error.html')
@zeit.web.view_config(
    name='komplettansicht',
    renderer='templates/komplettansicht.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    name='komplettansicht',
    renderer='templates/article_advertorial_komplett.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    name='komplettansicht',
    renderer='zeit.web.core:templates/paywall.html')
class Article(zeit.web.core.view_article.Article, zeit.web.site.view.Base):

    @zeit.web.reify
    def canonical_url(self):
        """ Canonical for komplettansicht is first page """
        if not self.is_all_pages_view:
            return super(Article, self).canonical_url
        else:
            return self.resource_url

    @zeit.web.reify
    def meta_keywords(self):
        return [x for x in ([self.ressort.title(), self.supertitle] +
                super(Article, self).meta_keywords) if x]

    # Only needed to set tracking code on
    # http://www.zeit.de/newsletter/registriert?nl=premium.
    @zeit.web.reify
    def newsletter_optin_tracking(self):
        return self.request.GET.get('newsletter-optin', None)

    @zeit.web.reify
    def storystream(self):
        if self.context.storystreams:
            return self.context.storystreams[0].references
        else:
            return None

    @zeit.web.reify
    def storystream_items(self):
        storystream_cp = self.storystream
        if not storystream_cp:
            return ()
        atoms = list(zeit.edit.interfaces.IElementReferences(storystream_cp))
        if self.context not in atoms:
            return atoms[:3]
        pos = atoms.index(self.context)
        if pos == 0:
            return atoms[:3]
        elif pos == len(atoms) - 1:
            return atoms[-3:]
        else:
            return atoms[pos - 1:pos + 2]

    def _get_solr_lineage(self, from_, to, sort, default):
        query = lq.and_(
            lq.datetime_range('date_first_released', from_, to),
            lq.bool_field('breaking_news', False),
            lq.field_raw('type', 'article'),
            lq.not_(lq.field('uniqueId', self.context.uniqueId)),
            lq.not_(lq.field('ressort', 'zeit-magazin')),
            lq.not_(lq.field('ressort', 'Campus')),
            lq.text_range('channels', None, None),
            lq.field_raw('product_id', lq.or_(
                'ZEDE', 'ZEI', 'ZECH', 'ZEC', 'ZEOE', 'ZES', 'ZTWI',
                'ZTGS', 'ZTCS', 'CSRG', 'ZSF', 'KINZ')),
            lq.field('published', 'published'))
        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        with zeit.web.core.metrics.timer('lineage.solr.reponse_time'):
            result = solr.search(
                query, sort='date_first_released {}'.format(sort),
                fl='title supertitle uniqueId', rows=1)
        if result.docs:
            return result.docs[0]
        else:
            return default

    def _get_lineage(self, from_, to, sort, default):
        must_clause = [{
            'range': {
                'payload.document.date_first_released': {
                    'gt': from_, 'lt': to
                }
            }
        }, {
            'term': {'payload.document.breaking_news': False}
        }, {
            'term': {'payload.document.access': 'free'}
        }, {
            'term': {'payload.meta.type': 'article'}
        }, {
            'exists': {'field': 'payload.document.channels'}
        }, {
            'terms': {'payload.workflow.product-id': [
                'ZEDE', 'ZEI', 'ZECH', 'ZEC', 'ZEOE', 'ZES', 'ZTWI',
                'ZTGS', 'ZTCS', 'CSRG', 'ZSF', 'KINZ']}
        }, {
            'term': {'payload.workflow.published': True}
        }]
        must_not_clause = [{
            'terms': {'payload.document.ressort': [
                'Administratives', 'zeit-magazin', 'Campus', 'Arbeit']}
        }]
        query = {
            'query': {
                'bool': {
                    'must': must_clause,
                    'must_not': must_not_clause
                }
            }
        }
        elasticsearch = zope.component.getUtility(
            zeit.retresco.interfaces.IElasticsearch)
        with zeit.web.core.metrics.timer('lineage.elasticsearch.reponse_time'):
            results = elasticsearch.search(
                query, 'payload.document.date_first_released:{}'.format(sort),
                rows=1, include_payload=True)
        if results:
            doc = results[0]
            return {
                'title': doc['payload']['body'].get('title'),
                'supertitle': doc['payload']['body'].get('supertitle'),
                'uniqueId': (
                    zeit.cms.interfaces.ID_NAMESPACE.rstrip('/') + doc['url'])}
        else:
            return default

    @zeit.web.reify('default_term')
    def lineage(self):
        if (self.is_advertorial or
            not self.context.channels or
            self.ressort == 'administratives' or
            self.paywall or
            zeit.content.article.interfaces.IErrorPage.providedBy(
                self.context)):
            return

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        date = info.date_first_released
        default = {
            'title': 'Startseite', 'supertitle': '',
            'uniqueId': 'http://xml.zeit.de/index'}

        if zeit.web.core.application.FEATURE_TOGGLES.find(
                'elasticsearch_lineage'):
            date = date.isoformat()
            predecessor = self._get_lineage('now-1y', date, 'desc', default)
            successor = self._get_lineage(date, 'now', 'asc', default)
        else:
            predecessor = self._get_solr_lineage(None, date, 'desc', default)
            successor = self._get_solr_lineage(date, None, 'asc', default)

        lineage = (predecessor, successor)

        if default in lineage:
            return zeit.web.dont_cache(lineage)

        return lineage

    @zeit.web.reify
    def include_optimizely(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('optimizely_on_zon_article', None)

    @zeit.web.reify
    def volumepage_is_published(self):
        cp = zeit.content.cp.interfaces.ICenterPage(self.volume, None)
        pubinfo = zeit.cms.workflow.interfaces.IPublishInfo(cp, None)
        return getattr(pubinfo, 'published', False)

    @zeit.web.reify
    def liveblog(self):
        return zeit.web.core.interfaces.ILiveblogInfo(self.context)

    @zeit.web.reify
    def advertising_in_article_body_enabled(self):
        if self.advertising_enabled:
            if self.liveblog.collapse_preceding_content:
                return False

        return super(Article, self).advertising_in_article_body_enabled


@zeit.web.view_defaults(vertical='zon')
@zeit.web.view_config(
    name='seite',
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    path_info='.*seite-(.*)',
    renderer='templates/article_advertorial.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    path_info='.*seite-(.*)',
    renderer='zeit.web.core:templates/paywall.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


def is_breaking_news(context, request):
    breaking = zeit.content.article.interfaces.IBreakingNews(context, None)
    if not (breaking and breaking.is_breaking):
        return False
    now = datetime.datetime.now(babel.dates.get_timezone('Europe/Berlin'))
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    seconds = zeit.web.core.utils.to_int(conf.get('breaking_news_timeout'))
    threshold = datetime.timedelta(seconds=seconds)
    return info and (now - info.date_first_released) < threshold


@zeit.web.view_config(
    vertical='zon',
    custom_predicates=(is_breaking_news,),
    renderer='templates/article_breaking.html')
class BreakingNews(Article):

    header_layout = 'breaking'


@zeit.web.view_defaults(
    context=zeit.web.core.article.IColumnArticle,
    vertical='zon')
@zeit.web.view_config(
    renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    name='komplettansicht',
    renderer='templates/komplettansicht.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    name='komplettansicht',
    renderer='zeit.web.core:templates/paywall.html')
class ColumnArticle(Article):

    header_layout = 'column'


@zeit.web.view_defaults(
    context=zeit.web.core.article.IColumnArticle,
    vertical='zon')
@zeit.web.view_config(
    name='seite',
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    path_info='.*seite-(.*)',
    renderer='zeit.web.core:templates/paywall.html')
class ColumnPage(zeit.web.core.view_article.ArticlePage, ColumnArticle):
    pass


@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_dpa_article,),
    # just render the first page because we expect only one page for DPA-news
    renderer='zeit.web.site:templates/article.html')
class DPAArticle(Article):

    header_layout = news_type = 'dpa'


@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_afp_article,),
    # just render the first page because we expect only one page for AFP-news
    renderer='zeit.web.site:templates/article.html')
class AFPArticle(Article):

    news_type = 'afp'


@zeit.web.view_config(
    context=zeit.web.core.article.ILiveblogArticle,
    renderer='templates/liveblog.html')
class LiveblogArticle(Article):

    header_layout = 'liveblog'


@zeit.web.view_config(
    route_name='amp',
    renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
    pass


@zeit.web.view_config(
    route_name='amp',
    context=zeit.web.core.article.ILiveblogArticle,
    renderer='templates/amp/liveblog.html')
class AcceleratedMobilePageLiveblogArticle(
        LiveblogArticle, AcceleratedMobilePageArticle):
    pass


class YahoofeedArticle(Article):

    truncated = False

    def truncate(self):

        allowed_article_length = 2000
        character_counter = 0

        for page in self.pages:
            for block in page.blocks[:]:
                if character_counter > allowed_article_length:
                    self.truncated = True
                    page.blocks.remove(block)

                if isinstance(block, zeit.web.core.block.Paragraph):
                    character_counter += len(block)
