# -*- coding: utf-8 -*-
import datetime
import logging

import babel.dates
import zope.component

import zeit.cms.workflow.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_article
import zeit.web.site.view


log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    custom_predicates=(zeit.web.site.view.is_zon_content,))
@zeit.web.view_config(
    renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_paywalled),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/article_advertorial.html')
@zeit.web.view_config(
    name='komplettansicht',
    renderer='templates/komplettansicht.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_advertorial),
    name='komplettansicht',
    renderer='templates/article_advertorial_komplett.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_paywalled),
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
        atoms = list(zeit.content.cp.interfaces.ICMSContentIterable(
            storystream_cp))
        if self.context not in atoms:
            return atoms[:3]
        pos = atoms.index(self.context)
        if pos == 0:
            return atoms[:3]
        elif pos == len(atoms) - 1:
            return atoms[-3:]
        else:
            return atoms[pos - 1:pos + 2]

    @zeit.web.reify
    def has_series_attached(self):
        return getattr(self.context, 'serie', None)

    @zeit.web.reify
    def series(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        uid = u'{}/{}'.format(
            conf.get('series_prefix', ''), self.context.serie.url)
        return zeit.cms.interfaces.ICMSContent(uid, None)

    @zeit.web.reify
    def include_optimizely(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('optimizely_on_zon_article', None)


@zeit.web.view_config(
    name='seite',
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_advertorial),
    path_info='.*seite-(.*)',
    renderer='templates/article_advertorial.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       zeit.web.core.view.is_paywalled),
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
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_breaking_news),
    renderer='templates/article_breaking.html')
class BreakingNews(Article):

    header_layout = 'breaking'


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article),
    renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article,
                       zeit.web.core.view.is_paywalled),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article),
    name='komplettansicht',
    renderer='templates/komplettansicht.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article,
                       zeit.web.core.view.is_paywalled),
    name='komplettansicht',
    renderer='zeit.web.core:templates/paywall.html')
class ColumnArticle(Article):

    header_layout = 'column'


@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article),
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.site.view.is_zon_content,
                       is_column_article,
                       zeit.web.core.view.is_paywalled),
    path_info='.*seite-(.*)',
    renderer='zeit.web.core:templates/paywall.html')
class ColumnPage(zeit.web.core.view_article.ArticlePage, ColumnArticle):
    pass


@zeit.web.view_config(
    context=zeit.web.core.article.ILiveblogArticle,
    renderer='templates/liveblog.html')
class LiveblogArticle(Article):

    header_layout = 'liveblog'

    @zeit.web.reify
    def liveblog(self):
        return zeit.web.core.interfaces.ILiveblogInfo(self.context)


@zeit.web.view_config(
    route_name='amp',
    renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):

    @zeit.web.reify
    def liveblog(self):
        return zeit.web.core.interfaces.ILiveblogInfo(self.context)


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
            for block in page:
                if character_counter > allowed_article_length:
                    self.truncated = True
                    page.blocks.remove(block)

                if isinstance(block, zeit.web.core.block.Paragraph):
                    character_counter += len(block)
