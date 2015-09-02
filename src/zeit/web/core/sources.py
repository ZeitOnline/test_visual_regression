import logging
import os
import os.path
import pkg_resources
import random
import re
import urlparse

import gocept.cache.method
import lxml.etree
import pysolr
import zope.interface

import zeit.cms.interfaces
import zeit.content.image.variant
import zeit.imp.source
import zeit.solr.interfaces

import zeit.web.core.interfaces
import zeit.web.core.utils
import zeit.web.core.view


video_series = None
log = logging.getLogger(__name__)


def get_video_series(series_source):
    try:
        series_xml = lxml.etree.parse(series_source)
    except (TypeError, IOError):
        return list()
    videoseries = series_xml.xpath('/allseries/videoseries/series')
    videoseries_list = list()
    for video in videoseries:
        url = video.xpath('@url')[0]
        title = video.xpath('@title')[0]
        videoseries_list.append(dict(url=url, title=title))
    return videoseries_list


def get_whitelist_meta(whitelist_meta_source):
    # try:
    #     meta_xml = lxml.etree.parse(whitelist_meta_source)
    # except (TypeError, IOError):
    #     return list()
    # meta = meta_xml.xpath('/tagReferences')
    # __import__("pdb").set_trace()
    # for meta_data in meta:
    #     meta = meta_data.xpath('/categoryReference')
    #     meta_list = list()

    #     url = data.xpath('@url')[0]
    #     title = data.xpath('@title')[0]
    #     meta_list.append(dict(url=url, title=title))
    return 'test'


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
                          'parquet-regular', 'parquet-spektrum',
                          'zon-parquet-small'],
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


class Solr(object):
    """Mock Solr implementation that is used for local development."""

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def search(self, q, rows=10, **kw):
        parts = urlparse.urlparse('egg://zeit.web.core/data')
        repo = pkg_resources.resource_filename(parts.netloc, parts.path[1:])
        results = []
        for root, subdirs, files in os.walk(repo):
            if not random.randint(0, 4):
                continue  # Skip some folders to speed things up.
            for filename in files:
                try:
                    assert not filename.endswith('meta')
                    unique_id = os.path.join(
                        root.replace(repo, 'http://xml.zeit.de'), filename)
                    content = zeit.cms.interfaces.ICMSContent(unique_id)
                    assert zeit.web.core.view.known_content(content)
                    results.append({
                        u'date_last_published': u'2015-07-01T09:50:42Z',
                        u'last-semantic-change': u'2015-07-01T09:50:42Z',
                        u'product_id': content.product.id,
                        u'supertitle': content.supertitle,
                        u'title': content.title,
                        u'type': content.__class__.__name__.lower(),
                        u'uniqueId': content.uniqueId
                    })
                except (AttributeError, AssertionError, TypeError):
                    continue
        return pysolr.Results(
            random.sample(results, min(rows, len(results))), len(results))

    def update_raw(self, xml, **kw):
        pass
