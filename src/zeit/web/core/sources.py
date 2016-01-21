import logging
import os
import os.path
import pkg_resources
import random
import re
import urllib
import urlparse
import xml.sax.saxutils

import pyramid.urldispatch
import pysolr
import zc.sourcefactory.source
import zc.sourcefactory.contextual
import zope.interface

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.image.variant
import zeit.imp.source
import zeit.solr.interfaces

import zeit.web.core.utils
import zeit.web.core.view


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


class VideoSeriesSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'series-source'

    def getValues(self):
        try:
            tree = self._get_tree()
        except (TypeError, IOError):
            return []
        videoseries = tree.xpath('/allseries/videoseries/series')
        result = []
        for node in videoseries:
            result.append(dict(url=node.get('url'), title=node.get('title')))
        return result

VIDEO_SERIES = VideoSeriesSource()


class ScaleSource(zeit.imp.source.ScaleSource):

    def isAvailable(self, *args):  # NOQA
        # Contrary to CMS behavior, we do not want to hide any image scales
        # in zeit.web, so availability is `True` regardless of context.
        return True

SCALE_SOURCE = ScaleSource()(None)


class ImageScales(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    # Only contextual so we can customize source_class

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def find(self, id):
            return self.factory.getValues(None).get(id)

    def getValues(self, context):
        def sub(x):
            return int(re.sub('[^0-9]', '', '0' + str(x)))

        return {s.name: (sub(s.width), sub(s.height)) for s in SCALE_SOURCE}

IMAGE_SCALE_SOURCE = ImageScales()(None)


class TeaserMapping(zeit.web.core.utils.frozendict):

    _map = {'zon-large': ['leader', 'leader-two-columns', 'leader-panorama',
                          'parquet-large', 'zon-parquet-large'],
            'zon-small': ['text-teaser', 'buttons', 'large', 'short', 'date',
                          'parquet-regular', 'zon-parquet-small'],
            'zon-fullwidth': ['leader-fullwidth'],
            'zon-inhouse': ['parquet-verlag'],
            'hide': ['archive-print-volume', 'archive-print-year',
                     'two-side-by-side', 'ressort', 'leader-upright',
                     'buttons-fullwidth', 'parquet-printteaser']}

    def __init__(self, *args, **kw):
        # Flattens and reverses _map, so we can easily lookup a layout.
        super(TeaserMapping, self).__init__(
            x for k, v in self._map.iteritems() for x in zip(v, [k] * len(v)))

TEASER_MAPPING = TeaserMapping()


class VariantSource(zeit.content.image.variant.VariantSource):

    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def find(self, context, variant_id):
        mapping = self._get_mapping()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue

            attributes = dict(node.attrib)
            mapped = mapping.get(variant_id, variant_id)

            if attributes['name'] == mapped:
                attributes['id'] = attributes['name']
                variant = zeit.content.image.variant.Variant(**attributes)
                if variant_id != mapped:
                    variant.legacy_name = variant_id
                return variant
        raise KeyError(variant_id)

    @CONFIG_CACHE.cache_on_arguments()
    def _get_mapping(self):
        return {k['old']: k['new'] for k in
                zeit.content.image.variant.LEGACY_VARIANT_SOURCE(None)}


VARIANT_SOURCE = VariantSource()


class BlacklistSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.web'
    config_url = 'blacklist-url'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def matches(self, path):
            return self.factory.matches(path)

    def matches(self, path):
        for matcher in self.compile_blacklist():
            if matcher(path) is not None:
                return True
        return False

    @CONFIG_CACHE.cache_on_arguments()
    def compile_blacklist(self):
        matchers = []
        for pattern in self.getValues(None):
            matcher, _ = pyramid.urldispatch._compile_route(pattern)
            matchers.append(matcher)
        return matchers


BLACKLIST_SOURCE = BlacklistSource()(None)


class RessortFolderSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = (
        zeit.cms.content.sources.SubNavigationSource.product_configuration)
    config_url = zeit.cms.content.sources.SubNavigationSource.config_url

    master_node_xpath = (
        zeit.cms.content.sources.SubNavigationSource.master_node_xpath)
    slave_tag = zeit.cms.content.sources.SubNavigationSource.slave_tag
    attribute = zeit.cms.content.sources.SubNavigationSource.attribute

    # Same idea as zeit.cms.content.sources.MasterSlavesource.getTitle()
    def find(self, ressort, subressort):
        tree = self._get_tree()
        if not subressort:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    master=xml.sax.saxutils.quoteattr(ressort)))
        else:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'
                u'/{slave_tag}[@{attribute} = {slave}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    slave_tag=self.slave_tag,
                    master=xml.sax.saxutils.quoteattr(ressort),
                    slave=xml.sax.saxutils.quoteattr(subressort)))
        if not nodes:
            return {}
        return zeit.cms.interfaces.ICMSContent(
            nodes[0].get('uniqueId'), {})

RESSORTFOLDER_SOURCE = RessortFolderSource()


class Solr(object):
    """Mock Solr implementation that is used for local development."""

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def search(self, q, rows=10, **kw):
        parts = urlparse.urlparse('egg://zeit.web.core/data')
        repo = pkg_resources.resource_filename(parts.netloc, parts.path[1:])
        results = []
        for root, subdirs, files in os.walk(repo):
            if not random.getrandbits(1):
                continue  # Skip some folders to speed things up.
            for filename in files:
                try:
                    name = filename.replace('.meta', '')
                    unique_id = os.path.join(
                        root.replace(repo, 'http://xml.zeit.de'), name)
                    content = zeit.cms.interfaces.ICMSContent(unique_id)
                    publish = zeit.cms.workflow.interfaces.IPublishInfo(
                        content)
                    semantic = zeit.cms.content.interfaces.ISemanticChange(
                        content)
                    assert zeit.web.core.view.known_content(content)
                    results.append({
                        u'date_last_published': (
                            publish.date_last_published.isoformat()),
                        u'date_first_released': (
                            publish.date_first_released.isoformat()),
                        u'last-semantic-change': (
                            semantic.last_semantic_change.isoformat()),
                        u'lead_candidate': False,
                        u'product_id': content.product.id,
                        u'supertitle': content.supertitle,
                        u'title': content.title,
                        u'type': content.__class__.__name__.lower(),
                        u'uniqueId': content.uniqueId
                    })
                except (AttributeError, AssertionError, TypeError):
                    continue

        log.debug('Mocking solr request ' + urllib.urlencode(
            kw.items() + [('q', q), ('rows', rows)], True))
        return pysolr.Results(
            random.sample(results, min(rows, len(results))), len(results))

    def update_raw(self, xml, **kw):
        pass


class FeatureToggleSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.web'
    config_url = 'feature-toggle-source'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def find(self, name):
            return self.factory.find(name)

    def find(self, name):
        try:
            return bool(getattr(self._get_tree(), name, False))
        except TypeError:
            return False

FEATURE_TOGGLE_SOURCE = FeatureToggleSource()(None)


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


class NavigationSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-source'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        @property
        def navigation(self):
            return self.factory.compile_navigation()

        @property
        def navigation_by_name(self):
            return self.factory.compile_navigation_by_name()

    @CONFIG_CACHE.cache_on_arguments()
    def compile_navigation(self):
        navigation = zeit.web.core.navigation.Navigation()
        root = self._get_tree()
        self._register_navigation_items(navigation, root.iterfind('section'))

        return navigation

    def _register_navigation_items(self, navigation, node):
        for section in node:
            item_id = section.find('link').get('id')
            text = section.find('link').text
            href = section.find('link').get('href')
            label = section.find('link').get('label') or None
            navigation[item_id] = zeit.web.core.navigation.NavigationItem(
                item_id, text, href, label)
            try:
                sub_sections_node = section.find(
                    'sub_sections').iterfind('sub_section')
                self._register_navigation_items(
                    navigation[item_id], sub_sections_node)
            except AttributeError:
                pass

    @CONFIG_CACHE.cache_on_arguments()
    def compile_navigation_by_name(self):
        navigation_links = zeit.web.core.navigation.Navigation()
        navigation = self.compile_navigation()
        for n in navigation:
            nav_item = navigation[n]
            navigation_links[nav_item.text.lower()] = {}
            navigation_links[nav_item.text.lower()]['link'] = nav_item.href
            navigation_links[nav_item.text.lower()]['text'] = nav_item.text

        return navigation_links

NAVIGATION_SOURCE = NavigationSource()(None)


class NavigationClassifiedsSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-classifieds-source'

NAVIGATION_CLASSIFIEDS_SOURCE = NavigationClassifiedsSource()(None)


class NavigationServicesSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-services-source'

NAVIGATION_SERVICES_SOURCE = NavigationServicesSource()(None)


class NavigationFooterPublisherSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-footer-publisher-source'

NAVIGATION_FOOTER_PUBLISHER_SOURCE = NavigationFooterPublisherSource()(None)


class NavigationFooterLinksSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-footer-links-source'

NAVIGATION_FOOTER_LINKS_SOURCE = NavigationFooterLinksSource()(None)
