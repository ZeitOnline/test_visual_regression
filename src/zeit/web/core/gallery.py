import collections

from grokcore.component import adapter, implementer
import zope.interface

import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image
import zeit.content.gallery.gallery

import zeit.web.core.block

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
class GalleryImage(zeit.web.core.block.Image):

    def __init__(self, item):
        self.caption = item.caption
        self.layout = 'large'  # item.layout
        self.title = item.title
        self.text = item.text

        if hasattr(item, 'image'):
            self.src = item.image.uniqueId
            self.uniqueId = item.image.uniqueId
            self.image = item.image

        def fix_uc(s):
            # Fix misrepresentation of latin-1 chars in unicode strings.
            if isinstance(s, unicode):
                try:
                    s = s.encode('latin-1', 'backslashreplace').decode('utf-8')
                except UnicodeDecodeError:
                    pass
            return s

        meta = zeit.content.image.interfaces.IImageMetadata(item)
        self.copyright = list((fix_uc(i[0]),) + i[1:] for i in meta.copyrights)
        self.alt = meta.alt
        self.align = meta.alignment


class Gallery(collections.OrderedDict):

    def __init__(self, context):
        super(Gallery, self).__init__([(k, IGalleryImage(v)) for k, v in
                                      context.items() if v.layout != 'hidden'])
        self.context = context

    def __repr__(self):
        return object.__repr__(self)

    @property
    def galleryText(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(
            self.context).html


@implementer(IGallery)
@adapter(zeit.content.gallery.interfaces.IGallery)
def standalone(context):
    cls = type('Standalone', (Gallery,), {})
    return cls(context)
