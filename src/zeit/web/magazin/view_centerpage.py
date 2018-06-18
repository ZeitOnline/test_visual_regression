import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.magazin.view


@zeit.web.view_defaults(
    context=zeit.content.cp.interfaces.ICenterPage,
    vertical='zmo')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/advertorial.html')
@zeit.web.view_config(
    renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view_centerpage.Centerpage,
                 zeit.web.magazin.view.Base):

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'ZMO'
