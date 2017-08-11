import zeit.content.gallery.interfaces

import zeit.web
import zeit.web.campus.view
import zeit.web.core.view_gallery


@zeit.web.view_config(
    context=zeit.content.gallery.interfaces.IGallery,
    vertical='zco',
    renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery,
              zeit.web.campus.view.Content):
    pass
