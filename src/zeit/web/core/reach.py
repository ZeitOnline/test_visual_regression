# -*- coding: utf-8 -*-
import logging

import requests
import requests.exceptions
import requests_file
import zope.component
import zope.interface

import zeit.cms.interfaces

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.metrics


log = logging.getLogger(__name__)


class Reach(object):

    zope.interface.implements(zeit.web.core.interfaces.IReach)

    session = requests.Session()

    def _get(self, location, **kw):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = u'{}/{}'.format(
            conf.get('linkreach_host'), location.encode('utf-8'))
        timeout = conf.get('reach_timeout', 0.2)
        try:
            with zeit.web.core.metrics.timer('http.reponse_time'):
                return self.session.get(url, params=kw, timeout=timeout).json()
        except (requests.exceptions.RequestException, ValueError), err:
            log.debug('Reach connection failed: {}'.format(err))

    def _get_ranking(self, location, facet=None, **kw):
        location = '.'.join(filter(bool, (location, facet)))
        kw.setdefault('limit', 3)
        docs = self._get('/'.join(('ranking', location)), **kw) or []
        for idx, doc in enumerate(docs):
            doc['product'] = NotImplemented
            doc['serie'] = NotImplemented
            doc['teaserTitle'] = doc.get('title')
            doc['teaserSupertitle'] = doc.get('supertitle')
            doc['access'] = doc.get('access', 'free')
            docs[idx] = zeit.cms.interfaces.ICMSContent(doc)
        return docs

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

    def get_buzz(self, unique_id='http://xml.zeit.de/index'):
        url = unique_id.replace(
            zeit.cms.interfaces.ID_NAMESPACE, 'http://www.zeit.de/', 1)
        return self._get('buzz', url=url) or {}


class MockReach(Reach):

    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())
