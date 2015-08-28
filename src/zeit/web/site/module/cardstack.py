import zeit.web


@zeit.web.register_module("cardstack")
class CardStack(zeit.web.site.module.Module):

    @zeit.web.reify
    def id(self):
        return self.context.card_id
