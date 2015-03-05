from pyramid.view import view_config

import zeit.web.core.view_gallery
import zeit.web.site.view


@view_config(context=zeit.web.core.gallery.IGallery,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    advertising_enabled = True
