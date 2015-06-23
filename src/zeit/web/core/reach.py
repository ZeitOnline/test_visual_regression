import logging

import requests
import requests.exceptions
import requests_file
import zope.component
import zope.interface

import zeit.cms.interfaces

import zeit.web.core.interfaces


log = logging.getLogger(__name__)


class Reach(object):

    zope.interface.implements(zeit.web.core.interfaces.IReach)

    host = zope.component.getUtility(
        zeit.web.core.interfaces.ISettings).get('linkreach_host', '')
    session = requests.Session()

    def _get(self, location, **kw):
        url = '{}/{}'.format(self.host, location)
        try:
            return self.session.get(url, params=kw, timeout=3.0).json()
        except (requests.exceptions.RequestException, ValueError), err:
            log.debug('Reach connection failed: {}'.format(err))

    def _get_ranking(self, location, facet=None, **kw):
        location = '.'.join(filter(bool, (location, facet)))
        kw.setdefault('limit', 3)
        return self._get('/'.join(('ranking', location)), **kw) or []

    def get_comments(self, **kw):
        return self._get_ranking('comments', **kw)

    def get_score(self, **kw):
        return self._get_ranking('score', **kw)

    def get_social(self, **kw):
        return self._get_ranking('social', **kw)

    def get_views(self, **kw):
        return self._get_ranking('views', **kw)

    def get_buzz(self, unique_id='http://xml.zeit.de/index'):
        url = unique_id.replace(
            'http://www.zeit.de/', zeit.cms.interfaces.ID_NAMESPACE, 1)
        return self._get('buzz', url=url) or {}


class MockReach(Reach):

    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())
