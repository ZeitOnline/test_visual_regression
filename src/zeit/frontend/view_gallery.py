import zeit.content.gallery.interfaces
import zeit.wysiwyg.interfaces
from pyramid.view import view_config


@view_config(context=zeit.content.gallery.interfaces.IGallery,
             renderer='templates/gallery.html')
class Gallery(zeit.frontend.view.Content):

    @property
    def images(self):
        return [self.context[i] for i in self.context]

    @property
    def galleryText(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.context).html

    # def __call__(self):
    #      import pdb;pdb.set_trace()
