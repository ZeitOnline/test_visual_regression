import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.block
import zeit.web.core.centerpage


class Buzzbox(zeit.web.core.block.Module, list):

    category = None
    header = None

    def __init__(self, context):
        super(Buzzbox, self).__init__(context)
        self += zeit.web.core.reach.fetch(self.category, self.ressort, 3)
        self.layout = 'buzz-{}'.format(self.category)

    @zeit.web.reify
    def ressort(self):
        centerpage = zeit.content.cp.interfaces.ICenterPage(self.context)
        return zeit.web.core.centerpage.get_ressort_id(centerpage)


@zeit.web.register_module('mostread')
class MostreadBuzzbox(Buzzbox):

    category = 'mostread'
    header = 'Meistgelesene Artikel'


@zeit.web.register_module('mostcommented')
class CommentsBuzzbox(Buzzbox):

    category = 'comments'
    header = 'Meistkommentiert'


@zeit.web.register_module('mostshared')
class FacebookBuzzbox(Buzzbox):

    category = 'facebook'
    header = 'Meistgeteilt'
