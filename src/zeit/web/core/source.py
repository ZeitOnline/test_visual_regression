import logging

import gocept.lxml.objectify

import zeit.cms.content.sources

import zeit.web.core.cache


CONFIG_CACHE = zeit.web.core.cache.get_region('config')
log = logging.getLogger(__name__)


def get_tree_from_url(self, url):
    try:
        return original_get(self, url)
    except Exception:
        log.warning('Error reading %s for %s', url, self, exc_info=True)
        return gocept.lxml.objectify.fromstring('<empty/>')
original_get = zeit.cms.content.sources.SimpleXMLSourceBase._get_tree_from_url
zeit.cms.content.sources.SimpleXMLSourceBase._get_tree_from_url = (
    get_tree_from_url)


class LigatusBlacklist(zeit.cms.content.sources.RessortSource):

    def getValues(self, context):
        return self._values()

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = []
        tree = self._get_tree()
        nodes = tree.xpath(
            '//ressort[@ligatus="no"] | //subnavigation[@ligatus="no"]')
        for node in nodes:
            result.append(node.get('name').lower())
        return result

LIGATUS_BLACKLIST = LigatusBlacklist()(None)
