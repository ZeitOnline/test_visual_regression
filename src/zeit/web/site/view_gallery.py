import pyramid.view

import zeit.web.core.view_gallery
import zeit.web.site.view


@pyramid.view.view_config(
    renderer='templates/gallery.html',
    context=zeit.content.gallery.interfaces.IGallery,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_method='GET')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    pass
