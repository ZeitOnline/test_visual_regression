from pyramid.view import view_config

import zeit.web.core.view_gallery
import zeit.web.site.view.Base


@view_config(context=zeit.content.article.interfaces.IGallery,
             custom_predicates=(zeit.web.site.view.is_zon_content,),
             renderer='templates/gallery.html')
class Gallery(zeit.web.core.view_gallery.Gallery, zeit.web.site.view.Base):
    advertising_enabled = True
