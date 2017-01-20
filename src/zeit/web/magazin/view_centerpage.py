import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.magazin.view


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/advertorial.html')
@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
    renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view_centerpage.Centerpage,
                 zeit.web.magazin.view.Base):

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'ZMO'
