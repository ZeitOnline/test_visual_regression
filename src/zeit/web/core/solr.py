import collections
import logging
import os
import os.path
import pkg_resources
import random
import urllib
import urlparse

import pyramid.threadlocal
import pysolr
import requests.sessions
import zope.component
import zope.component.globalregistry
import zope.interface.adapter
import zope.site.site

import zeit.cms.workflow.interfaces
import zeit.solr.interfaces
import zeit.solr.connection

import zeit.web.core.interfaces


log = logging.getLogger(__name__)


# Allow pysolr error handling to deal with non-ascii HTML error pages,
# see <https://bugs.python.org/issue11033>.
def scrape_response_nonascii(self, headers, response):
    if isinstance(response, str):
        response = response.decode('utf-8')
    if isinstance(response, unicode):
        response = response.encode('ascii', errors='ignore')
    return original_scrape_response(self, headers, response)
original_scrape_response = pysolr.Solr._scrape_response
pysolr.Solr._scrape_response = scrape_response_nonascii


# Make solr timeout runtime configurable
def solr_timeout_from_settings(self):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get('solr_timeout', 5)
zeit.solr.connection.SolrConnection.timeout = property(
    solr_timeout_from_settings, lambda self, value: None)


class ISitemapSolrConnection(zeit.solr.interfaces.ISolr):
    """
    Solr connection which handles requests for sitemaps.
    """


@zope.interface.implementer(ISitemapSolrConnection)
class SitemapSolrConnection(zeit.solr.connection.SolrConnection):

    """
    This solr connection uses a different timeout,
    which is necessary for generating sitemaps.
    """

    def __init__(self):
        config = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = config.get('vivi_zeit.solr_solr-url')
        self.ignore_search_errors = bool(
            config.get('solr-ignore-search-errors'))
        super(SitemapSolrConnection, self).__init__(url)

    @property
    def timeout(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('solr_sitemap_timeout', 10)

    # We need this setter because psysolr.Solr wants to set the timeout
    # in its __init__
    @timeout.setter
    def timeout(self, value):
        pass


class AdapterRegistry(zope.component.globalregistry.GlobalAdapterRegistry):
    """Accepts both Local and Global AdapterRegistry objects as bases, so it
    works both for published and preview mode (since the latter makes use of
    zodb-persisted local registries).

    It's not entirely clear where the actual mismatch occurs between
    zope.component/zope.interface/zope.site, and whether it would be
    resolveable generically, but at least for our specific use case this
    workaround turns out just fine.
    """

    def _setBases(self, bases):
        old = self.__dict__.get('__bases__', ())
        for r in old:
            if r not in bases:
                if hasattr(r, '_removeSubregistry'):
                    r._removeSubregistry(self)
        for r in bases:
            if r not in old:
                if hasattr(r, '_addSubregistry'):
                    r._addSubregistry(self)
        # Skip direct superclass, whose method we have copied&patched here.
        super(zope.interface.adapter.AdapterRegistry, self)._setBases(bases)


class SiteManager(zope.component.globalregistry.BaseGlobalComponents):

    def _init_registries(self):
        self.adapters = AdapterRegistry(self, 'adapters')
        self.utilities = AdapterRegistry(self, 'utilities')


def register_sitemap_solr_utility():
    """
    Register the ISitemapSolrConnection utility as ISolr utility.
    """
    # Dont use the gsm
    site = zope.site.site.SiteManagerContainer()
    registry = SiteManager(
        name='sitemaps_manager',
        bases=(zope.component.getSiteManager(),))
    sitemap_solr = zope.component.getUtility(ISitemapSolrConnection)
    site.setSiteManager(registry)
    registry.registerUtility(sitemap_solr, zeit.solr.interfaces.ISolr)
    zope.component.hooks.setSite(site)


def solr_send_request_with_referrer(self, *args, **kw):
    headers = kw.setdefault('headers', {})
    request = pyramid.threadlocal.get_current_request()
    headers['Referer'] = request.url
    headers['User-Agent'] = requests.utils.default_user_agent(
        'zeit.web-%s/pysolr/python-requests' % request.registry.settings.get(
            'version', 'unknown'))
    return original_send_request(self, *args, **kw)
original_send_request = pysolr.Solr._send_request
pysolr.Solr._send_request = solr_send_request_with_referrer


# Skip superfluous disk accesses, since we never use netrc for authentication.
requests.sessions.get_netrc_auth = lambda *args, **kw: None


# Test helpers ##############################


class RandomContent(object):

    def _get_content(self):
        import zeit.web.core.view  # Prevent circular import
        parts = urlparse.urlparse('egg://zeit.web.core/data')
        repo = pkg_resources.resource_filename(parts.netloc, parts.path[1:])
        for root, subdirs, files in os.walk(repo):
            if not random.getrandbits(1):
                continue  # Skip some folders to speed things up.
            for filename in files:
                name = filename.replace('.meta', '')
                unique_id = os.path.join(
                    root.replace(repo, 'http://xml.zeit.de'), name)
                content = zeit.cms.interfaces.ICMSContent(unique_id, None)
                if zeit.web.core.view.known_content(content):
                    yield content


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
class DataSolr(RandomContent):
    """Fake Solr implementation that is used for local development."""

    def search(self, q, rows=10, **kw):
        log.debug('Mocking solr request ' + urllib.urlencode(
            kw.items() + [('q', q), ('rows', rows)], True))
        results = []
        for content in self._get_content():
            try:
                publish = zeit.cms.workflow.interfaces.IPublishInfo(
                    content)
                modified = zeit.cms.workflow.interfaces.IModified(
                    content)
                semantic = zeit.cms.content.interfaces.ISemanticChange(
                    content)
                data = {
                    u'authors': content.authors,
                    u'comments': content.commentsAllowed,
                    u'date-last-modified': (
                        modified.date_last_modified.isoformat()),
                    u'date_first_released': (
                        publish.date_first_released.isoformat()),
                    u'date_last_published': (
                        publish.date_last_published.isoformat()),
                    u'date_last_published_semantic': (
                        publish.date_last_published_semantic.isoformat()),
                    u'keyword': [tag.label for tag in content.keywords],
                    u'keyword_id': [tag.url_value for tag in content.keywords],
                    u'last-semantic-change': (
                        semantic.last_semantic_change.isoformat()),
                    u'image-base-id': [
                        'http://xml.zeit.de/zeit-online/'
                        'image/filmstill-hobbit-schlacht-fuenf-hee/'],
                    u'product_id': content.product.id,
                    u'supertitle': content.supertitle,
                    u'teaser_supertitle': content.teaserSupertitle,
                    u'teaser_text': content.teaserText,
                    u'teaser_title': content.teaserTitle,
                    u'title': content.title,
                    u'type': content.__class__.__name__.lower(),
                    u'uniqueId': content.uniqueId
                }
                if 'fl' in kw:
                    for key in list(data.keys()):
                        if key not in kw['fl']:
                            del data[key]
                results.append(data)
            except (AttributeError, TypeError):
                continue
        return pysolr.Results(
            [random.choice(results) for x in range(rows)], len(results))

    def update_raw(self, xml, **kw):
        pass
