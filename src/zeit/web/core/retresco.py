import collections
import logging
import random

import grokcore.component
import lxml.etree
import mock
import pkg_resources
import zope.interface

import zeit.retresco.connection
import zeit.retresco.convert
import zeit.retresco.interfaces
import zeit.retresco.search

import zeit.web.core.solr


log = logging.getLogger(__name__)

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
