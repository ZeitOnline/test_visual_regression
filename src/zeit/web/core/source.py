import logging

import gocept.lxml.objectify

import zeit.cms.content.sources


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
