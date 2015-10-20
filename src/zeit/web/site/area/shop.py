import zope.schema

import zeit.content.cp.interfaces


@zeit.web.register_area('shop')
class Shop(zeit.web.site.area.gallery.Gallery):
    pass
