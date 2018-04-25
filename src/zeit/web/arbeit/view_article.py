import zeit.content.article.interfaces

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
              zeit.web.arbeit.view.Content):

    @zeit.web.reify
    def header_layout(self):
        if zeit.web.core.template.column(self.context):
            return 'column'
        return self.context.header_layout or 'default'


@zeit.web.view_defaults(vertical='zar')
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


@zeit.web.view_config(
    context=zeit.content.article.edit.interfaces.ICitation,
    vertical='*',  # only works if context provides ICMSContent
    name='sharequote',
    renderer='templates/inc/blocks/citation_zar-sharequote_standalone.html')
class Citation(Article):

    def __init__(self, context, request):
        # Change context to the article, so the superclass view properties work
        super(Citation, self).__init__(
            zeit.content.article.interfaces.IArticle(context), request)
        self.module = context

    def __call__(self):
        super(Citation, self).__call__()
        return {
            # pyramid's rendering is independent of view class instantiation,
            # and thus is unaffected by our change of self.context.
            'context': self.context,
            'module': zeit.web.core.interfaces.IArticleModule(self.module),
        }
