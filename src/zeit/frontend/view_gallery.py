import zeit.content.gallery.interfaces
from pyramid.view import view_config


@view_config(context=zeit.content.gallery.interfaces.IGallery,
             renderer='templates/gallery.html')
class Gallery(zeit.frontend.view.Content):

    @property
    def images(self):
        return [self.context[i] for i in self.context]
