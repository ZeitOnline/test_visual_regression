import zeit.web


@zeit.web.register_area('shop')
class Shop(zeit.web.site.area.gallery.Gallery):
    pass
