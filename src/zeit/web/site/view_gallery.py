import pyramid.view

import zeit.web.core.view_gallery
import zeit.web.site.view


@pyramid.view.view_config(
    renderer='templates/gallery.html',
    context=zeit.web.core.gallery.IGallery,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_method='GET')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    advertising_enabled = True

    @zeit.web.reify
    def banner_type(self):
        return 'gallery'

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Gallery, self).breadcrumbs
        self.breadcrumbs_by_navigation(breadcrumbs)
        return breadcrumbs
