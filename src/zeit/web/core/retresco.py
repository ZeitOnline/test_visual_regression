import collections
import logging
import random

import grokcore.component
import lxml.etree
import mock
import pkg_resources
import pyramid.threadlocal
import requests
import requests.utils
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
def is_healthy(self):
    """Cached health check, so we avoid additional requests that not only
    unecessarily take time just to return erroneous, but also add to the load
    of an already down server."""
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    timeout = float(conf.get('tms_timeout', 0.5))
    response = None
    try:
        with zeit.web.core.metrics.timer(
                'zeit.retresco.connection.health_check.tms.reponse_time'):
            response = requests.get(
                self.url + '/_system/check', timeout=timeout)
        response.raise_for_status()
        return True
    except Exception:
        log.warning('Health check failed', exc_info=True)
        return False
    finally:
        status = response.status_code if response else 599
        zeit.web.core.metrics.increment(
            'zeit.retresco.connection.health_check.tms.status.%s' % status)


zeit.retresco.connection.TMS.is_healthy = is_healthy


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
            'zeit.retresco.connection.tms.reponse_time'):
        return original_request(self, *args, **kw)


original_request = zeit.retresco.connection.TMS._request
zeit.retresco.connection.TMS._request = tms_request


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
