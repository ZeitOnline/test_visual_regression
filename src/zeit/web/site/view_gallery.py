from pyramid.view import view_defaults
from pyramid.view import view_config

import zeit.web.core.view_gallery
import zeit.web.site.view


@view_defaults(context=zeit.web.core.gallery.IGallery,
               custom_predicates=(zeit.web.site.view.is_zon_content,))
@view_config(renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    advertising_enabled = True

@view_defaults(context=zeit.web.core.gallery.IGallery,
               custom_predicates=(zeit.web.site.view.is_zon_content,),
               renderer='templates/inc/comments/comment-form.html')
@view_config(request_param='form=comment')
@view_config(request_param='form=report')
class CommentForm(zeit.web.core.view_gallery.Gallery):
    pass
