import zeit.content.gallery.interfaces

import zeit.web.core.view_gallery
import zeit.web.site.view


@zeit.web.view_config(
    context=zeit.content.gallery.interfaces.IGallery,
    vertical='zon',
    renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    pass
