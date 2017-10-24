import logging

import requests
import zope.interface

import zeit.web.core.interfaces
import zeit.web.core.metrics


log = logging.getLogger(__name__)


class Recaptcha(object):

    zope.interface.implements(zeit.web.core.interfaces.ICaptcha)

    RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'

    def verify(self, captcha_response):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        response = None
        try:
            with zeit.web.core.metrics.timer('http.reponse_time'):
                response = requests.post(self.RECAPTCHA_URL, timeout=1, data={
                    'secret': conf.get('recaptcha_secret_key'),
                    'response': captcha_response,
                })
            response.raise_for_status()
            return bool(response.json()['success'])
        except Exception:
            log.warning('Validating recaptcha failed', exc_info=True)
            return False
        finally:
            status = response.status_code if response else 599
            zeit.web.core.metrics.increment('http.status.%s' % status)
