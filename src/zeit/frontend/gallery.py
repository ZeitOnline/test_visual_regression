import collections

from grokcore.component import adapter, implementer
import zope.interface

import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image
import zeit.content.gallery.gallery

import zeit.frontend.block

# Custom interface classes to destinguish between regular galleries (inline
# or standalone) and product galleries.


class IGallery(zope.interface.Interface):

    iterkeys = zope.interface.Attribute('iterkeys')
    itervalues = zope.interface.Attribute('itervalues')


class IProductGallery(zope.interface.Interface):
    pass


class IGalleryImage(zope.interface.Interface):
    pass


@implementer(IGalleryImage)
@adapter(zeit.content.gallery.interfaces.IGalleryEntry)
class GalleryImage(zeit.frontend.block.Image):

    def __init__(self, item):
        self.caption = item.caption
        self.layout = 'large'  # item.layout
        self.title = item.title
        self.text = item.text

        if hasattr(item, 'image'):
            self.src = item.image.uniqueId
            self.uniqueId = item.image.uniqueId
            self.image = item.image
        image_meta = zeit.content.image.interfaces.IImageMetadata(item)
        # TODO: get complete list of copyrights with links et al
        # this just returns the first copyright without link
        # mvp it is
        self.copyright = [copyright[0]
                          for copyright in image_meta.copyrights][0]
        self.alt = image_meta.alt
        self.align = image_meta.alignment


class Gallery(collections.OrderedDict):

    def __init__(self, context):
        super(Gallery, self).__init__([(k, IGalleryImage(v)) for k, v in
                                      context.items() if v.layout != 'hidden'])

    def __repr__(self):
        return object.__repr__(self)


@implementer(IGallery)
@adapter(zeit.content.gallery.interfaces.IGallery)
def standalone(context):
    cls = type('Standalone', (Gallery,), {})
    return cls(context)
