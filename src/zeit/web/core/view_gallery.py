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
                    image=zeit.web.core.template.create_url(
                        None, i.image.uniqueId, self.request),
                    link=image_meta.copyrights[0][1],
                    nofollow=image_meta.copyrights[0][2]
                )
            )
        return sorted(teaser_list, key=lambda k: k['label'])
