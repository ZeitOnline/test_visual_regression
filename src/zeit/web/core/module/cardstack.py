import zeit.web
import zeit.content.article.edit.interfaces
import grokcore.component


@zeit.web.register_module("cardstack")
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICardstack)
class CardStack(zeit.web.core.centerpage.Module):
    pass
