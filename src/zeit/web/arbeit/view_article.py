import zeit.content.article.interfaces

import zeit.web
import zeit.web.arbeit.view
import zeit.web.core.view_article


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    custom_predicates=(zeit.web.arbeit.view.is_zar_content,))
@zeit.web.view_config(renderer='templates/article.html')
class Article(zeit.web.core.view_article.Article,
              zeit.web.arbeit.view.Content):

    @zeit.web.reify
    def article_layout(self):
        return 'default'


class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass
