import zeit.content.article.interfaces

import zope.component

import zeit.web
import zeit.web.arbeit.view
import zeit.web.core.view_article


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    vertical='zar')
@zeit.web.view_config(renderer='templates/article.html')
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
class Article(zeit.web.core.view_article.Article,
              zeit.web.arbeit.view.Content):

    @zeit.web.reify
    def article_layout(self):
        return 'default'

    # TODO: Move to core
    @zeit.web.reify
    def series(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        uid = u'{}/{}'.format(
            conf.get('series_prefix', ''), self.context.serie.url)
        return zeit.cms.interfaces.ICMSContent(uid, None)


@zeit.web.view_defaults(vertical='zar')
@zeit.web.view_config(
    name='seite',
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    path_info='.*seite-(.*)',
    renderer='zeit.web.core:templates/paywall.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@zeit.web.view_defaults(
    context=zeit.web.core.article.IColumnArticle,
    vertical='zar')
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
