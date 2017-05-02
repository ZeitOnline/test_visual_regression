import grokcore.component
import lxml.objectify
import zope.component
import zope.interface
import pyramid.httpexceptions
import zeit.content.gallery.interfaces
import zeit.content.article.edit.reference
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.view


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


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(
    zeit.content.gallery.interfaces.IVisibleEntryCount)
def article_gallery_image_count(context):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    for block in body.values():
        if zeit.content.article.edit.interfaces.IGallery.providedBy(block):
            return zeit.content.gallery.interfaces.IVisibleEntryCount(
                block.references, 0)
