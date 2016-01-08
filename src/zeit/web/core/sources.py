import logging
import os
import os.path
import pkg_resources
import random
import re
import urllib
import urlparse
import xml.sax.saxutils

import gocept.cache.method
import pysolr
import zope.interface

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.image.variant
import zeit.imp.source
import zeit.solr.interfaces

import zeit.web.core.interfaces
import zeit.web.core.utils
import zeit.web.core.view


video_series = None
log = logging.getLogger(__name__)


class VideoSeriesSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'series-source'

    def getValues(self):
        try:
            xml = self._get_tree()
        except (TypeError, IOError):
            return []
        videoseries = xml.xpath('/allseries/videoseries/series')
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


class ImageScales(zeit.web.core.utils.frozendict):

    zope.interface.implements(zeit.web.core.interfaces.IImageScales)

    def __init__(self, *args, **kw):
        def sub(x):
            return int(re.sub('[^0-9]', '', '0' + str(x)))

        scales = {s.name: (sub(s.width), sub(s.height)) for s in
                  ScaleSource()('')}
        super(ImageScales, self).__init__(scales)


class TeaserMapping(zeit.web.core.utils.frozendict):

    zope.interface.implements(zeit.web.core.interfaces.ITeaserMapping)

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

    @gocept.cache.method.Memoize(600, ignore_self=True)
    def _get_mapping(self):
        return {k['old']: k['new'] for k in
                zeit.content.image.variant.LEGACY_VARIANT_SOURCE(None)}


VARIANT_SOURCE = VariantSource()


class BlacklistSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'blacklist-url'


BLACKLIST_SOURCE = BlacklistSource()


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


class FeatureToggleSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'feature-toggle-source'

    def find(self, name):
        try:
            return bool(getattr(self._get_tree(), name, False))
        except TypeError:
            return False

FEATURE_TOGGLE_SOURCE = FeatureToggleSource()
