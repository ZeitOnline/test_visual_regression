from pyramid.view import view_config

import zeit.web.core.gallery
import zeit.web.magazin.view


@view_config(context=zeit.web.core.gallery.IGallery,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/gallery.html')
class Gallery(zeit.web.core.view.Content, zeit.web.magazin.view.Base):
    advertising_enabled = True


@view_config(context=zeit.web.core.gallery.IProductGallery,
             renderer='templates/product.html')
class ProductGallery(Gallery):
    pass
