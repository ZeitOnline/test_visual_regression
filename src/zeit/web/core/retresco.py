import collections
import logging
import random

from gocept.cache.property import TransactionBoundCache
import grokcore.component
import lxml.etree
import mock
import pkg_resources
import pyramid.threadlocal
import requests
import requests.utils
import urllib3
import zope.interface

import zeit.retresco.connection
import zeit.retresco.convert
import zeit.retresco.interfaces
import zeit.retresco.search

import zeit.web.core.cache
import zeit.web.core.metrics
import zeit.web.core.solr


SHORT_TERM_CACHE = zeit.web.core.cache.get_region('short_term')
log = logging.getLogger(__name__)


@SHORT_TERM_CACHE.cache_on_arguments()
def is_tms_healthy(self):
    """Cached health check, so we avoid additional requests that not only
    unecessarily take time just to return erroneous, but also add to the load
    of an already down server."""
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    timeout = float(conf.get('tms_timeout', 0.5))
    response = None
    try:
        with zeit.web.core.metrics.http(
                'zeit.retresco.connection.health_check.tms') as record:
            response = requests.get(
                self.url + '/health-check', timeout=timeout)
            record(response)
        response.raise_for_status()
        return True
    except Exception:
        log.warning('Health check failed', exc_info=True)
        return False


zeit.retresco.connection.TMS.is_healthy = is_tms_healthy


def tms_request(self, *args, **kw):
    """Adds health check, metrics and referrer."""
    if not self.is_healthy():
        raise zeit.retresco.interfaces.TechnicalError('Health check failed')
    headers = kw.setdefault('headers', {})
    request = pyramid.threadlocal.get_current_request()
    headers['Referer'] = request.url
    headers['User-Agent'] = requests.utils.default_user_agent(
        'zeit.web-%s/retresco/python-requests' % request.registry.settings.get(
            'version', 'unknown'))
    with zeit.web.core.metrics.timer(
            'zeit.retresco.connection.tms.response_time'):
        return original_request(self, *args, **kw)


original_request = zeit.retresco.connection.TMS._request
zeit.retresco.connection.TMS._request = tms_request


def cached_intextlink_data(self, content, timeout):
    """Cache TMS response until the end of the request.
    This mainly prevents request duplication from get_article_body and
    get_article_keywords, which are both used when displaying an IArticle page.
    """
    if content.uniqueId not in self._intextlink_data:
        response = orig_get_intextlink_data(self, content, timeout)
        self._intextlink_data[content.uniqueId] = response
    return self._intextlink_data[content.uniqueId]


orig_get_intextlink_data = zeit.retresco.connection.TMS._get_intextlink_data
zeit.retresco.connection.TMS._get_intextlink_data = cached_intextlink_data
zeit.retresco.connection.TMS._intextlink_data = TransactionBoundCache(
    '_v_intextlink_data', dict)


def es_user_agent(self):
    return 'zeit.web-%s/retresco/python-urllib3-%s' % (
        pkg_resources.get_distribution('zeit.web').version,
        urllib3.__version__)


zeit.retresco.search.Connection._user_agent = es_user_agent


@SHORT_TERM_CACHE.cache_on_arguments()
def is_es_healthy(self):
    """Cached health check, so we avoid additional requests that not only
    unecessarily take time just to return erroneous, but also add to the load
    of an already down server."""
    metrics = zope.component.getUtility(zeit.web.core.interfaces.IMetrics)
    try:
        with zeit.web.core.metrics.timer(
                'zeit.retresco.search.health_check'
                '.elasticsearch.response_time'):
            original_es_request(self, 'GET', '/')
        metrics.increment(
            'zeit.retresco.search.health_check.elasticsearch.status.200')
        return True
    except Exception:
        log.warning('Health check failed', exc_info=True)
        metrics.increment(
            'zeit.retresco.search.health_check.elasticsearch.status.599')
        return False


zeit.retresco.search.Connection.is_healthy = is_es_healthy


def es_request(self, *args, **kw):
    if not self.is_healthy():
        raise zeit.retresco.interfaces.TechnicalError('Health check failed')
    with zeit.web.core.metrics.timer(
            'zeit.retresco.search.elasticsearch.response_time'):
        return original_es_request(self, *args, **kw)


original_es_request = zeit.retresco.search.Connection.perform_request
zeit.retresco.search.Connection.perform_request = es_request


# Test helpers ##############################


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
class DataTMS(
        zeit.retresco.connection.TMS,
        zeit.web.core.solr.RandomContent):
    """Fake TMS implementation that is used for local development."""

    def __init__(self):
        self._response = collections.defaultdict(tuple)

    def _request(self, request, **kw):
        return self._response

    def get_topicpages(self, start=0, rows=25):
        xml = lxml.etree.parse(pkg_resources.resource_stream(
            'zeit.web.core', 'data/config/topicpages.xml'))
        topics = list(xml.getroot().iterchildren('topic'))
        result = zeit.cms.interfaces.Result()
        result.hits = len(topics)
        try:
            for topic in topics[start:start + rows]:
                result.append({
                    'id': topic.get('id'),
                    'type': topic.get('type'),
                    'title': topic.text,
                })
        except IndexError:
            pass
        return result

    def get_topicpage_documents(self, id, start=0, rows=25, filter=None):
        log.debug(
            'Mocking TMS request id=%s, start=%s, rows=%s', id, start, rows)
        result = []
        for content in self._get_content():
            data = zeit.retresco.interfaces.ITMSRepresentation(content)()
            if data is not None:
                # Ensure we always have an image
                data['payload'].setdefault('head', {}).setdefault(
                    'teaser_image',
                    'http://xml.zeit.de/zeit-online/'
                    'image/filmstill-hobbit-schlacht-fuenf-hee/')
                result.append(data)
        self._response = {
            'num_found': len(result),
            'docs': random.sample(result, rows),
        }
        result = super(DataTMS, self).get_topicpage_documents(id, start, rows)
        self._response = {}
        print result
        return result


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class DataES(
        zeit.retresco.search.Elasticsearch,
        zeit.web.core.solr.RandomContent):
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
                data['payload'].setdefault('head', {}).setdefault(
                    'teaser_image',
                    'http://xml.zeit.de/zeit-online/'
                    'image/filmstill-hobbit-schlacht-fuenf-hee/')
                if not include_payload:
                    del data['payload']
                result.append({'_source': data})

        self._response = {'hits': {
            'total': len(result),
            'hits': random.sample(result, rows),
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
