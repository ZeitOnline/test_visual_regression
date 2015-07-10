import pyramid.view

import zeit.web.core.view_gallery
import zeit.web.site.view


@pyramid.view.view_defaults(
    context=zeit.web.core.gallery.IGallery,
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_method='GET')
@pyramid.view.view_config(renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    advertising_enabled = True

    @zeit.web.reify
    def banner_type(self):
        return 'gallery'


@pyramid.view.view_config(name='comment-form',
                          renderer='templates/inc/comments/comment-form.html')
@pyramid.view.view_config(name='report-form',
                          renderer='templates/inc/comments/report-form.html')
class CommentForm(Gallery):
    pass
