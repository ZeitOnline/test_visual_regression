import zeit.content.article.interfaces

import zeit.web
import zeit.web.campus.view
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_article


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    vertical='zco')
@zeit.web.view_config(renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/article_advertorial.html')
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
class Article(zeit.web.core.view_article.Article,
              zeit.web.campus.view.Content):

    @zeit.web.reify
    def article_layout(self):
        if zeit.web.core.template.column(self.context):
            return 'column'
        elif zeit.web.core.template.leserartikel(self.context):
            return 'leserartikel'
        elif self.header_layout != 'default':
            return self.header_layout
        else:
            return 'default'


@zeit.web.view_defaults(vertical='zco')
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


@zeit.web.view_config(
    route_name='amp',
    renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
    pass
