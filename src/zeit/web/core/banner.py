import zope.interface

import zc.sourcefactory.source

import zeit.web.core.interfaces
import zeit.web.core.cache


CONFIG_CACHE = zeit.web.core.cache.get_region('config')


@zope.interface.implementer(zeit.web.core.interfaces.IPlace)
class Place(object):

    """A place is a space on the website, which can be filled with a banner."""

    def __init__(self, tile, type, on_page_nr=None):
        self.tile = tile
        self.type = type
        self.on_page_nr = on_page_nr


@zope.interface.implementer(zeit.web.core.interfaces.IContentAdBlock)
class ContentAdBlock(object):

    """A space for an iqd content ad"""

    def __init__(self, name):
        self.name = name


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
