import requests
import requests.exceptions
import requests_file
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


banner_list = None
iqd_mobile_ids = None
banner_id_mappings = None


def make_banner_list(banner_config):
    if not banner_config:
        return []
    # XXX requests does not seem to allow to mount stuff as a default, sigh.
    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())
    banner_list = []
    try:
        banner_file = session.get(banner_config, stream=True, timeout=2)
        # Analoguous to requests.api.request().
        session.close()
    except requests.exceptions.RequestException:
        return banner_list
    root = lxml.objectify.parse(banner_file.raw).getroot()
    for place in root.place:
        try:
            sizes = str(place.multiple_sizes).strip().split(',')
        except AttributeError:
            sizes = [str(place.width) + 'x' + str(place.height)]
        try:
            diuqilon = place.diuqilon
        except AttributeError:
            diuqilon = False
        try:
            adlabel = place.adlabel
        except AttributeError:
            adlabel = None
        try:
            dcopt = place.dcopt
        except AttributeError:
            dcopt = None
        banner_list.append(Place(
            place.tile, sizes, diuqilon, adlabel,
            min_width=place.min_width, active=place.get('active'),
            dcopt=dcopt))
    return sorted(banner_list, key=lambda place: place.tile)


def make_iqd_mobile_ids(banner_config):
    if not banner_config:
        return {}
    # XXX requests does not seem to allow to mount stuff as a default, sigh.
    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())
    iqd_mobile_ids = {}
    try:
        banner_file = session.get(banner_config, stream=True, timeout=2)
        # Analoguous to requests.api.request().
        session.close()
    except requests.exceptions.RequestException:
        return iqd_mobile_ids
    root = lxml.objectify.parse(banner_file.raw).getroot()
    for iqd_id in root.iqd_id:
        try:
            iqd_mobile_ids[iqd_id.get('ressort')] = IqdMobileList(iqd_id)
        except:
            pass
    return iqd_mobile_ids


def make_banner_id_mappings(banner_id_mappings_source):
    try:
        banner_id_mappings_xml = lxml.etree.parse(banner_id_mappings_source)
    except (TypeError, IOError):
        return list()
    banner_id_mappings = banner_id_mappings_xml.xpath(
        '/banner_id_mappings/mapping')
    mapping_list = list()
    for mapping in banner_id_mappings:
        target = mapping.xpath('@target')[0]
        value = mapping.xpath('@value')[0]
        banner_code = mapping.xpath('@banner_code')[0]
        mapping_list.append(
            dict(target=target, value=value, banner_code=banner_code))
    return mapping_list
