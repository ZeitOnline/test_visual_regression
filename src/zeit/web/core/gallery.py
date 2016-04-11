import collections

import grokcore.component
import zope.interface

import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image
import zeit.content.gallery.gallery

import zeit.web.core.block
import zeit.web.core.template
import zeit.web.core.utils

# Custom interface classes to destinguish between regular galleries (inline
# or standalone) and product galleries.


class IGallery(zope.interface.Interface):

    iterkeys = zope.interface.Attribute('iterkeys')
    itervalues = zope.interface.Attribute('itervalues')


class IProductGallery(zope.interface.Interface):
    pass


class IGalleryImage(zope.interface.Interface):
    pass


@grokcore.component.implementer(IGalleryImage)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
class GalleryImage(zeit.web.core.image.BaseImage):

    def __init__(self, item):
        self.layout = item.layout or 'large'
        self.image_pattern = 'zon-large'
        self.title = item.title
        self.text = item.text

        if hasattr(item, 'image'):
            self.src = item.image.uniqueId
            self.uniqueId = item.image.uniqueId
            self.image = item.image

        meta = zeit.content.image.interfaces.IImageMetadata(item.image)
        fix_ml = zeit.web.core.utils.fix_misrepresented_latin
        self.copyright = list((fix_ml(i[0]),) + i[1:] for i in meta.copyrights)
        self.alt = meta.alt
        self.caption = item.caption


@zeit.web.register_global
def get_gallery_image(module=None, content=None, **kwargs):
    # XXX Re-implement once we have a solution for RepositoryImage variants.

    if content is None:
        content = zeit.web.core.template.first_child(module)

    if content is None:
        return

    return zeit.web.core.template.first_child(Gallery(content).itervalues())


class Gallery(collections.OrderedDict):

    def __init__(self, context):
        entries = []
        for key in context.keys():
            try:
                value = context[key]
            except:
                continue
            else:
                if value.layout == 'hidden':
                    continue
                entries.append((key, IGalleryImage(value)))
        super(Gallery, self).__init__(entries)
        self.context = context

    def __repr__(self):
        return object.__repr__(self)

    @property
    def galleryText(self):  # NOQA
        return zeit.wysiwyg.interfaces.IHTMLContent(
            self.context).html


@grokcore.component.implementer(IGallery)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
def standalone(context):
    cls = type('Standalone', (Gallery,), {})
    return cls(context)
