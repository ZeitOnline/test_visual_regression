# -*- coding: utf-8 -*-
import logging

import requests
import requests.exceptions
import requests_file
import zope.component
import zope.interface

import zeit.retresco.interfaces

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.metrics
import zeit.web.core.repository


log = logging.getLogger(__name__)
DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')


class Reach(object):

    zope.interface.implements(zeit.web.core.interfaces.IReach)

    session = requests.Session()

    def _get(self, location, **kw):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = u'{}/{}'.format(
            conf.get('linkreach_host'), location.encode('utf-8'))
        timeout = conf.get('reach_timeout', 0.2)
        response = None
        try:
            with zeit.web.core.metrics.http('http') as record:
                response = self.session.get(url, params=kw, timeout=timeout)
                record(response)
            return response.json()
        except (requests.exceptions.RequestException, ValueError), err:
            log.debug('Reach connection failed: {}'.format(err))

    def _get_ranking(self, location, facet=None, **kw):
        location = '.'.join(filter(bool, (location, facet)))
        kw.setdefault('limit', 3)
        docs = self._get('/'.join(('ranking', location)), **kw) or []
        result = []
        for doc in docs:
            content = self._resolve(doc)
            if content is None:
                continue
            # XXX Should we instead use an adapter to expose this?
            # Templates currently don't care and simply say `teaser.score`
            content.score = doc.get('score')
            result.append(content)
        return result

    def _resolve(self, doc):
        try:
            result = self._get_metadata(doc['location'])
            content = zeit.retresco.interfaces.ITMSContent(result[0])
        except Exception:
            log.warning('Resolving %s failed', doc, exc_info=True)
            return None
        zeit.web.core.repository.add_marker_interfaces(
            content, in_repository=False)
        return content

    @DEFAULT_TERM_CACHE.cache_on_arguments(should_cache_fn=bool)
    def _get_metadata(self, path):
        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        return es.search({'query': {'term': {'url': path}}},
                         rows=1, include_payload=True)

    def get_comments(self, **kw):
        return self._get_ranking('comments', **kw)

    def get_score(self, **kw):
        return self._get_ranking('score', **kw)

    def get_trend(self, **kw):
        return self._get_ranking('trend', **kw)

    def get_social(self, **kw):
        return self._get_ranking('social', **kw)

    def get_views(self, **kw):
        return self._get_ranking('views', **kw)


class MockReach(Reach):

    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())

    def _get_metadata(self, path):
        content = zeit.cms.interfaces.ICMSContent(u'http://xml.zeit.de' + path)
        return [zeit.retresco.interfaces.ITMSRepresentation(content)()]
