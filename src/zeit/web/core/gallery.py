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


class IGallery(zope.interface.Interface):
    pass


class IGalleryImage(zope.interface.Interface):
    pass


@grokcore.component.implementer(IGalleryImage)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
class GalleryImage(zeit.web.core.image.BaseImage):

    def __init__(self, item):
        self.layout = item.layout or 'large'
        self.image_pattern = 'original'
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
        return None

    for key in content.keys():
        try:
            value = content[key]
        except:
            continue
        else:
            if value.layout == 'hidden':
                continue
            return IGalleryImage(value)
    return None


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
    def html(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(
            self.context).html


@grokcore.component.implementer(IGallery)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
def standalone(context):
    cls = type('Standalone', (Gallery,), {})
    return cls(context)
