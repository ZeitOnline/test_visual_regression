import zeit.frontend.gallery
import zeit.wysiwyg.interfaces
from pyramid.decorator import reify
from pyramid.view import view_config


@view_config(context=zeit.frontend.gallery.IGallery,
             renderer='templates/gallery.html')
class Gallery(zeit.frontend.view.Content):

    advertising_enabled = True

    def __call__(self):
        self.context.advertising_enabled = self.advertising_enabled
        return {}

    @reify
    def images(self):
        return [self.context[i] for i in self.context]

    @reify
    def galleryText(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.context).html


@view_config(context=zeit.frontend.gallery.IProductGallery,
             renderer='templates/product.html')
class ProductGallery(Gallery):
    pass
