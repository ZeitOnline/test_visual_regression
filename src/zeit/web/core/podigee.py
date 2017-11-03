import logging

import requests
import zope.interface

import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.metrics


MEDIUM_TERM_CACHE = zeit.web.core.cache.get_region('medium_term')
log = logging.getLogger(__name__)


class Podigee(object):
    """API Documentation: https://app.podigee.com/api-docs"""

    zope.interface.implements(zeit.web.core.interfaces.IPodigee)

    def get_episode(self, id):
        result = self._api_request('/episodes/{}'.format(id))
        result.setdefault('podcast_id', 'null')
        return result

    def get_podcast(self, id):
        return self._api_request('/podcasts/{}'.format(id))

    @MEDIUM_TERM_CACHE.cache_on_arguments(should_cache_fn=lambda x: x)
    def _api_request(self, path):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = '{}/{}'.format(conf.get('podigee_url'), path)
        response = None
        try:
            with zeit.web.core.metrics.timer('api.http.reponse_time'):
                response = requests.get(
                    url, headers={'Token': conf.get('podigee_token')},
                    timeout=conf.get('podigee_api_timeout', 2))
                return response.json()
        except Exception:
            log.warning('API GET %s failed', path, exc_info=True)
            return {}
        finally:
            status = response.status_code if response else 599
            zeit.web.core.metrics.increment('api.http.status.%s' % status)

    @MEDIUM_TERM_CACHE.cache_on_arguments(should_cache_fn=lambda x: x)
    def get_player_configuration(self, url):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        response = None
        try:
            with zeit.web.core.metrics.timer('config.http.reponse_time'):
                response = requests.get(
                    url + u'/embed?context=external',
                    headers={'Accept': 'application/json'},
                    timeout=conf.get('podigee_config_timeout', 2))
            data = response.json()
            try:
                # By disabling the "playlist" feature of the podigee player
                # (which we're not using), we can drastically shrink the JSON.
                del data['podcast']['episodes']
            except KeyError:
                pass
            return data
        except Exception:
            log.warning('config GET %s failed', url, exc_info=True)
            return {}
        finally:
            status = response.status_code if response else 599
            zeit.web.core.metrics.increment('config.http.status.%s' % status)
