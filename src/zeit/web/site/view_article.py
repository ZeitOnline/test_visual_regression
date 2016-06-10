# -*- coding: utf-8 -*-
import datetime
import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
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


@view_defaults(context=zeit.content.article.interfaces.IArticle,
               custom_predicates=(zeit.web.site.view.is_zon_content,),
               request_method='GET')
@view_config(renderer='templates/article.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
             zeit.web.core.view.is_advertorial),
             renderer='templates/article_advertorial.html')
@view_config(name='komplettansicht',
             renderer='templates/komplett.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
             zeit.web.core.view.is_advertorial),
             name='komplettansicht',
             renderer='templates/article_advertorial_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.site.view.Base):

    @zeit.web.reify
    def canonical_url(self):
        """ Canonical for komplettansicht is first page """
        if not self.is_all_pages_view:
            return super(Article, self).canonical_url
        else:
            return self.resource_url

    @zeit.web.reify
    def extend_from_template(self):
        return "zeit.web.site:templates/article.html"

    @zeit.web.reify
    def embed_header(self):
        embed_header = zeit.content.article.edit.interfaces.IHeaderArea(
            self.context).module
        if embed_header:
            return zeit.web.core.interfaces.IFrontendBlock(embed_header)

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
    def has_series_attached(self):
        return getattr(self.context, 'serie', None)

    @zeit.web.reify
    def series(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        uid = u'{}/{}'.format(
            conf.get('series_prefix', ''), self.context.serie.url)
        return zeit.cms.interfaces.ICMSContent(uid, None)


@view_config(name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
@view_config(name='seite',
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                zeit.web.core.view.is_advertorial),
             path_info='.*seite-(.*)',
             renderer='templates/article_advertorial.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@view_config(route_name='amp',
             renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
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


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_breaking_news),
             renderer='templates/article_breaking.html')
class BreakingNews(Article):
    pass


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


def has_author_image(context, request):
    authors = zeit.web.core.article.convert_authors(context)
    if not authors:
        return False
    # XXX Should use proper variant, cf. z.w.core.template.get_column_image.
    return zeit.web.core.template.get_variant(
        authors[0]['image_group'], 'original')


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             renderer='templates/column.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             name='komplettansicht',
             renderer='templates/komplett.html')
class ColumnArticle(Article):

    @zeit.web.reify
    def extend_from_template(self):
        return "zeit.web.site:templates/column.html"

    @zeit.web.reify
    def author_img(self):
        return has_author_image(self.context, self.request)

    @zeit.web.reify
    def sharing_image(self):
        if not self.authors:
            return
        return self.authors[0]['image_group']


@view_config(name='seite',
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             path_info='.*seite-(.*)',
             renderer='templates/column.html')
class ColumnPage(zeit.web.core.view_article.ArticlePage, ColumnArticle):
    pass


@view_config(context=zeit.web.core.article.ILiveblogArticle,
             renderer='templates/liveblog.html')
class LiveblogArticle(Article):

    def __init__(self, *args, **kwargs):
        super(LiveblogArticle, self).__init__(*args, **kwargs)
        self.liveblog_last_modified = self.date_last_modified
        self.liveblog_is_live = False
        for page in self.pages:
            for block in page.blocks:
                if isinstance(block, zeit.web.core.block.Liveblog):
                    self.liveblog_is_live = block.is_live
                    if block.last_modified:
                        self.liveblog_last_modified = block.last_modified
                    # break the inner loop
                    break
            else:
                # continue if the inner loop wasn't broken
                continue
            # inner loop was broken, break the outer
            break
