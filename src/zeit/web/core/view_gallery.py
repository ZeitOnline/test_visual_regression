import lxml.objectify
import zope.component
import zope.interface

import zeit.content.image.interfaces

import zeit.web


class Gallery(zeit.web.core.view.Content):

    @zeit.web.reify
    def gallery(self):
        # We synthesize a gallery reference block to reuse the block template
        block = zeit.content.article.edit.reference.Gallery(
            self.context, lxml.objectify.E.gallery(href=self.context.uniqueId))
        return zeit.web.core.interfaces.IFrontendBlock(block)

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Gallery, self).breadcrumbs
        self.breadcrumbs_by_navigation(breadcrumbs)
        self.breadcrumbs_by_title(breadcrumbs)
        return breadcrumbs

    @zeit.web.reify
    def webtrekk_assets(self):
        return ['gallery.0/seite-1']


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.image.interfaces.IPersistentThumbnail)
def persistent_thumbnail_factory(context):
    """Disable vivi-only functionality, especially since creating content does
    not work in our environment.
    """
    return object()
