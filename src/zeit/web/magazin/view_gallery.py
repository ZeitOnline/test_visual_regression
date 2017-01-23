import zeit.content.gallery.interfaces

import zeit.web
import zeit.web.core.view_gallery
import zeit.web.magazin.view


@zeit.web.view_config(
    context=zeit.content.gallery.interfaces.IGallery,
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
    renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.magazin.view.Base):

    @zeit.web.reify
    def banner_type(self):
        return 'article'
