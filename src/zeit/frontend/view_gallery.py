from pyramid.view import view_config

import zeit.wysiwyg.interfaces

import zeit.frontend
import zeit.frontend.gallery


@view_config(context=zeit.frontend.gallery.IGallery,
             renderer='templates/gallery.html')
class Gallery(zeit.frontend.view.Content):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Gallery, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.advertising_enabled

    @zeit.frontend.reify
    def images(self):
        # TODO: Why does this not work with zope interfaces?
        return zeit.frontend.gallery.standalone(self.context)

    @zeit.frontend.reify
    def galleryText(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.context).html

    @zeit.frontend.reify
    def banner_type(self):
        return 'article'

    @property
    def copyrights(self):
        teaser_list = []
        for i in self.images.values():
            image_meta = zeit.content.image.interfaces.IImageMetadata(i.image)
            if (len(image_meta.copyrights) < 1 or
                    len(image_meta.copyrights[0][0]) <= 1):
                # Drop teaser if no copyright text is assigned.
                continue
            teaser_list.append(
                dict(
                    label=image_meta.copyrights[0][0],
                    image=zeit.frontend.template.translate_url(
                        i.image.uniqueId),
                    link=image_meta.copyrights[0][1],
                    nofollow=image_meta.copyrights[0][2]
                )
            )
        return sorted(teaser_list, key=lambda k: k['label'])


@view_config(context=zeit.frontend.gallery.IProductGallery,
             renderer='templates/product.html')
class ProductGallery(Gallery):
    pass
