import pyramid.view

import zeit.content.article.interfaces

import zeit.web.campus.view
import zeit.web.core.view_article


@pyramid.view.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    custom_predicates=(zeit.web.campus.view.is_zco_content,),
    request_method='GET')
@pyramid.view.view_config(renderer='templates/article.html')
@pyramid.view.view_config(name='komplettansicht',
                          renderer='templates/komplett.html')
class Article(
        zeit.web.core.view_article.Article, zeit.web.campus.view.Base):
    pass
