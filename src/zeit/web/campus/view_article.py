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
class Article(zeit.web.core.view_article.Article, zeit.web.campus.view.Base):

    @zeit.web.reify
    def article_layout(self):
        if zeit.web.core.template.column(self.context):
            return 'column'
        elif zeit.web.core.template.leserartikel(self.context):
            return 'leserartikel'
        else:
            return 'default'

    @zeit.web.reify
    def topic_page(self):
        try:
            return zeit.campus.interfaces.ITopic(self.context).page
        except TypeError:
            return None

    @zeit.web.reify
    def topic_label(self):
        try:
            topic = zeit.campus.interfaces.ITopic(self.context)
        except TypeError:
            return ''
        if topic.label:
            return topic.label
        return getattr(topic.page, 'title', '')


@pyramid.view.view_config(name='seite',
                          path_info='.*seite-(.*)',
                          renderer='templates/article.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass
