import logging

from pyramid.view import view_config

import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_article


log = logging.getLogger(__name__)


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             request_method='GET',
             renderer='templates/article.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             name='komplettansicht',
             renderer='templates/article_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.site.view.Base):
    pass


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             name='comment-form',
             renderer='templates/inc/comments/comment-form.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             name='report-comment-form',
             renderer='templates/inc/comments/report-comment-form.html')
class CommentForm(zeit.web.core.view_article.Article):
    pass


def is_breaking_news(context, request):
    return zeit.content.article.interfaces.IBreakingNews(context).is_breaking


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_breaking_news),
             renderer='templates/breaking_news_article.html')
class BreakingNews(zeit.web.core.view_article.Article,
                   zeit.web.site.view.Base):
    pass


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article),
             renderer='templates/column.html')
class ColumnArticle(Article, zeit.web.core.view_article.Article):
    pass
