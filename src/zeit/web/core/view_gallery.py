import zeit.wysiwyg.interfaces

import zeit.web

import zeit.web.magazin.view


class Gallery(zeit.web.core.view.Content):

    advertising_enabled = True

    def __init__(self, *args, **kwargs):
        super(Gallery, self).__init__(*args, **kwargs)
        self.context.advertising_enabled = self.advertising_enabled

    @zeit.web.reify
    def gallery(self):
        return zeit.web.core.block.Gallery(self.context)

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
