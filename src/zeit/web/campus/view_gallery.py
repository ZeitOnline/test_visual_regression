import pyramid.view

import zeit.web.campus.view
import zeit.web.core.view_gallery


@pyramid.view.view_config(
    renderer='templates/gallery.html',
    context=zeit.content.gallery.interfaces.IGallery,
    custom_predicates=(zeit.web.campus.view.is_zco_content,),
    request_method='GET')
class Gallery(zeit.web.core.view_gallery.Gallery,
              zeit.web.campus.view.Content):

    advertising_enabled = True

    @zeit.web.reify
    def banner_type(self):
        return 'gallery'
