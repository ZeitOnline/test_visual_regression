import lxml.objectify
import zope.interface

import zeit.web.core.interfaces


@zope.interface.implementer(zeit.web.core.interfaces.IPlace)
class Place(object):

    """A place is a space on the website, which can be filled with a banner.

    :param str tile: Tilenumber as supplied in iqd speech
    :param list sizes: In the form 'widthxheight' i.e. '728x90'
    :param bool diuqilon: Sets negative keyword targeting
    :param str label: Label to be shown above the ad
    :keyword int min_width: Window width negativ keyword targeting
                            is applied to, defaults to 0 (no min-width)
    :keyword bool active: Deactivate the place by configuration if needed
    :keyword str dcopt: Iqd keyword, defaults to 'ist'
    """

    def __init__(self, tile, sizes, diuqilon, label,
                 min_width=0, active=True, dcopt='ist'):
        self.name = 'tile_' + str(tile)
        self.tile = tile
        self.sizes = sizes
        self.diuqilon = diuqilon
        self.min_width = min_width
        self.dcopt = dcopt
        if label is not None:
            self.label = label
        if not isinstance(self.sizes, list) or self.sizes[0] is None:
            raise IndexError('Invalid sizes array')
        self.noscript_width_height = self.sizes[0].split('x')


@zope.interface.implementer(zeit.web.core.interfaces.IContentAdBlock)
class ContentAdBlock(object):

    """A space for an iqd content ad"""

    def __init__(self, name):
        self.name = name


@zope.interface.implementer(zeit.web.core.interfaces.IIqdMobileList)
class IqdMobileList(object):

    def __init__(self, iqd_id):
        self.centerpage = {}
        self.gallery = {}
        self.article = {}
        self.default = {}
        self.ressort = iqd_id.get('ressort')
        # Set ids for alle page types
        self.set_ids(iqd_id, 'centerpage')
        self.set_ids(iqd_id, 'gallery')
        self.set_ids(iqd_id, 'article')
        self.set_ids(iqd_id, 'default')

    def set_ids(self, iqd_id, page_type):
        if hasattr(iqd_id, page_type):
            # Set ids for all positions
            getattr(self, page_type)['top'] = \
                getattr(iqd_id, page_type).get('top')
            getattr(self, page_type)['middle'] = \
                getattr(iqd_id, page_type).get('middle')
            getattr(self, page_type)['bottom'] = \
                getattr(iqd_id, page_type).get('bottom')
