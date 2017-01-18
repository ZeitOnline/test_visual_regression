import zeit.content.gallery.interfaces

import zeit.web
import zeit.web.campus.view
import zeit.web.core.view_gallery


@zeit.web.view_config(
    renderer='templates/gallery.html',
    context=zeit.content.gallery.interfaces.IGallery,
    custom_predicates=(zeit.web.campus.view.is_zco_content,))
class Gallery(zeit.web.core.view_gallery.Gallery,
              zeit.web.campus.view.Content):
    pass
