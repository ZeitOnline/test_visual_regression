import zope.interface

import zc.sourcefactory.source

import zeit.web.core.interfaces
import zeit.web.core.cache


CONFIG_CACHE = zeit.web.core.cache.get_region('config')


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
            raise IndexError('Invalid sizes list')
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


class BruceBannerSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'banner-source'

    @CONFIG_CACHE.cache_on_arguments()
    def getValues(self, context):
        banner_list = []

        for place in self._get_tree().iterfind('place'):
            sizes = place.find('multiple_sizes')
            if sizes:
                sizes = sizes.text.strip().split(',')
            else:
                width = place.find('width').text
                height = place.find('height').text
                sizes = ['{}x{}'.format(width, height)]

            diuqilon = True if place.find('diuqilon') else False
            adlabel = place.find('adlabel').text if (
                place.find('adlabel')) else None
            dcopt = place.find('dcopt').text if place.find('dcopt') else None
            banner_list.append(
                zeit.web.core.banner.Place(
                    place.tile,
                    sizes,
                    diuqilon,
                    adlabel,
                    min_width=place.find('min_width').text,
                    active=place.get('active'),
                    dcopt=dcopt))
        return sorted(banner_list, key=lambda place: place.tile)

BANNER_SOURCE = BruceBannerSource()(None)


class IqdMobileIdsSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'iqd-mobile-ids-source'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        @property
        def ids(self):
            return self.factory.compile_ids()

    @CONFIG_CACHE.cache_on_arguments()
    def compile_ids(self):
        iqd_mobile_ids = {}
        for iqd_id in self._get_tree().iterfind('iqd_id'):
            try:
                iqd_mobile_ids[iqd_id.get('ressort')] = (
                    zeit.web.core.banner.IqdMobileList(iqd_id))
            except:
                pass
        return iqd_mobile_ids

IQD_MOBILE_IDS_SOURCE = IqdMobileIdsSource()(None)


class BannerIdMappingsSource(
        zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'banner-id-mappings-source'

    @CONFIG_CACHE.cache_on_arguments()
    def getValues(self, context):
        mapping_list = list()
        for mapping in self._get_tree().iterfind('mapping'):
            target = mapping.get('target')
            value = mapping.get('value')
            banner_code = mapping.get('banner_code')
            mapping_list.append(
                dict(target=target, value=value, banner_code=banner_code))
        return mapping_list

BANNER_ID_MAPPINGS_SOURCE = BannerIdMappingsSource()(None)
