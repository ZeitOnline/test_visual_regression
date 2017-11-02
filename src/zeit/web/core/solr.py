import logging
import os
import os.path
import pkg_resources
import random
import urllib
import urlparse

import grokcore.component
import mock
import pyramid.threadlocal
import pysolr
import requests.sessions
import zope.component

import zeit.cms.workflow.interfaces
import zeit.solr.interfaces
import zeit.retresco.connection
import zeit.retresco.convert
import zeit.retresco.interfaces
import zeit.retresco.search

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
pysolr.Solr.timeout = property(
    solr_timeout_from_settings, lambda self, value: None)


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


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
class DataTMS(zeit.retresco.connection.TMS, RandomContent):
    """Fake TMS implementation that is used for local development."""

    def __init__(self):
        self._response = {}

    def _request(self, request, **kw):
        return self._response

    def get_topicpage_documents(self, id, start=0, rows=25):
        log.debug(
            'Mocking TMS request id=%s, start=%s, rows=%s', id, start, rows)
        result = []
        for content in self._get_content():
            data = zeit.retresco.interfaces.ITMSRepresentation(content)()
            if data is not None:
                # Ensure we always have an image
                data['payload'].setdefault(
                    'teaser_image',
                    'http://xml.zeit.de/zeit-online/'
                    'image/filmstill-hobbit-schlacht-fuenf-hee/')
                # XXX LazyProxy cannot support liveblogs, and we don't want to
                # expose those in tests.
                data['payload']['is_live'] = False
                result.append(data)
        self._response = {
            'num_found': len(result),
            'docs': [random.choice(result) for x in range(rows)],
        }
        result = super(DataTMS, self).get_topicpage_documents(id, start, rows)
        self._response = {}
        print result
        return result


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class DataES(zeit.retresco.search.Elasticsearch, RandomContent):
    """Fake elasticsearch implementation that is used for local development."""

    def __init__(self):
        self._response = {}
        self.client = mock.Mock()
        self.client.search = self._search
        self.index = None

    def search(
            self, query, sort_order, start=0, rows=25, include_payload=False):
        result = []
        for content in self._get_content():
            data = zeit.retresco.interfaces.ITMSRepresentation(content)()
            if data is not None:
                # Ensure we always have an image
                data['payload'].setdefault(
                    'teaser_image',
                    'http://xml.zeit.de/zeit-online/'
                    'image/filmstill-hobbit-schlacht-fuenf-hee/')
                # XXX LazyProxy cannot support liveblogs, and we don't want to
                # expose those in tests.
                data['payload']['is_live'] = False
                if not include_payload:
                    del data['payload']
                result.append({'_source': data})

        self._response = {'hits': {
            'total': len(result),
            'hits': [random.choice(result) for x in range(rows)],
        }}
        result = super(DataES, self).search(
            query, sort_order, start, rows, include_payload)
        self._response = {}
        return result

    def _search(self, *args, **kw):
        return self._response


class CMSSearch(zeit.retresco.convert.Converter):

    interface = zeit.cms.interfaces.ICMSContent
    grokcore.component.name('zeit.find')

    def __call__(self):
        # Disable vivi-specific Converter, as it does not work without Zope.
        return {}
