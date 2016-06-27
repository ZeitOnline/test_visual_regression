from pyramid.view import view_config
import zope.component

import zeit.cms.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.magazin.interfaces
import zeit.seo

import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_centerpage
import zeit.web.magazin.view


@view_config(context=zeit.content.cp.interfaces.ICP2015,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                                zeit.web.core.view.is_advertorial),
             renderer='templates/advertorial.html')
@view_config(context=zeit.content.cp.interfaces.ICP2015,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view_centerpage.Centerpage,
                 zeit.web.magazin.view.Base):

    @zeit.web.reify
    def is_hp(self):
        return self.context.type == 'ZMO'
