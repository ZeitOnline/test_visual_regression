import zeit.wysiwyg.interfaces

import zeit.web
import zeit.web.core.gallery

import zeit.web.magazin.view


class Gallery(zeit.web.core.view.Content):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Gallery, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.advertising_enabled

    @zeit.web.reify
    def images(self):
        # TODO: Why does this not work with zope interfaces?
        return zeit.web.core.gallery.standalone(self.context)

    @zeit.web.reify
    def galleryText(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.context).html

    @zeit.web.reify
    def banner_type(self):
        return 'article'
