import collections

from grokcore.component import adapter, implementer
import zope.interface

import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image
import zeit.content.gallery.gallery

import zeit.frontend.block

# Custom interface classes to destinguish between regular galleries (inline
# or standalone) and product galleries.


class IGallery(zeit.content.gallery.interfaces.IGallery):
    pass


class IProductGallery(zeit.content.gallery.interfaces.IGallery):
    pass
