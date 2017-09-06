import logging

import requests
import zope.interface

import zeit.web.core.interfaces
import zeit.web.core.metrics


log = logging.getLogger(__name__)


class Podigee(object):

    zope.interface.implements(zeit.web.core.interfaces.IPodigee)

    def get_episode(self, id):
        result = self._request('/episodes/{}'.format(id))
        return result


    def _request(self, path):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = '{}/{}'.format(conf.get('podigee_url'), path)
        try:
            with zeit.web.core.metrics.timer('http.reponse_time'):
                return requests.get(
                    url, headers={'Token': conf.get('podigee_token')},
                    timeout=conf.get('podigee_timeout', 2)).json()
        except Exception:
            log.warning('GET %s failed', path, exc_info=True)
            return {}
