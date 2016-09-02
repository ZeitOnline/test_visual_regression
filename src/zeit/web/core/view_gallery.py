import lxml.objectify

import zeit.wysiwyg.interfaces

import zeit.web
import zeit.web.magazin.view


class Gallery(zeit.web.core.view.Content):

    advertising_enabled = True

    def __init__(self, context, request):
        super(Gallery, self).__init__(context, request)
        self.context.advertising_enabled = self.advertising_enabled

    @zeit.web.reify
    def gallery(self):
        # We synthesize a gallery reference block to reuse the block template
        block = zeit.content.article.edit.reference.Gallery(
            self.context, lxml.objectify.E.gallery(href=self.context.uniqueId))
        return zeit.web.core.interfaces.IFrontendBlock(block)

    @zeit.web.reify
    def banner_type(self):
        return 'article'

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Gallery, self).breadcrumbs
        self.breadcrumbs_by_navigation(breadcrumbs)
        self.breadcrumbs_by_title(breadcrumbs)
        return breadcrumbs

    @zeit.web.reify
    def webtrekk_assets(self):
        return ['gallery.0/seite-1']
