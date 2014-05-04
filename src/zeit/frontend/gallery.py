import zeit.content.gallery.interfaces

# Custom interface classes to destinguish between regular galleries (inline
# or standalone) and product galleries.


class IGallery(zeit.content.gallery.interfaces.IGallery):
    pass


class IProductGallery(zeit.content.gallery.interfaces.IGallery):
    pass
