import zeit.web
import zeit.web.core.article
import zeit.content.article.edit.interfaces
import grokcore.component


@zeit.web.register_module("cardstack")
@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICardstack)
class CardStack(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def id(self):
        return self.context.card_id
