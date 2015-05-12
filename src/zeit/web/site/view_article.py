import logging

from pyramid.view import view_config
from pyramid.view import view_defaults

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


@view_defaults(context=zeit.content.article.interfaces.IArticle,
               custom_predicates=(zeit.web.site.view.is_zon_content,),
               request_method='GET')
@view_config(renderer='templates/article.html')
@view_config(name='komplettansicht',
             renderer='templates/article_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.site.view.Base):

    @zeit.web.reify
    def canonical_url(self):
        """ Canonical for komplettansicht is first page """
        return self.resource_url


@view_config(name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@view_config(request_param='form=comment',
             renderer='templates/inc/comments/comment-form.html')
@view_config(request_param='form=report',
             renderer='templates/inc/comments/report-form.html')
class CommentForm(Article):
    pass


def is_breaking_news(context, request):
    return zeit.content.article.interfaces.IBreakingNews(context).is_breaking


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_breaking_news),
             renderer='templates/breaking_news_article.html')
class BreakingNews(Article):
    pass


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article),
             renderer='templates/column.html')
class ColumnArticle(Article):
    pass
