import pyramid.view

import zeit.content.article.interfaces

import zeit.web.campus.view
import zeit.web.core.template
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

    @zeit.web.reify
    def type(self):
        if zeit.web.core.template.column(self.context):
            return 'column'
        elif zeit.web.core.template.leserartikel(self.context):
            return 'leserartikel'
        else:
            return super(Article, self).type
