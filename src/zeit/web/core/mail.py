import logging

import requests
import zope.interface

import zeit.web.core.interfaces


log = logging.getLogger(__name__)


class MailJet(object):

    zope.interface.implements(zeit.web.core.interfaces.IMail)

    def send(self, from_, to, subject, body):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        # See <https://dev.mailjet.com/guides/#send-transactional-email>
        data = {'Messages': [{
            'From': {'Name': 'Kontaktformular',
                     'Email': conf['mailjet_sender']},
            'To': [{'Email': to}],
            'Subject': subject[:255],
            'TextPart': body,
        }]}
        if from_ and '@' in from_:
            data['Messages'][0]['ReplyTo'] = {'Email': from_}
        self._request('POST /send', body=data)

    def _request(self, request, body=None):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        verb, path = request.split(' ')
        method = getattr(requests, verb.lower())
        url = conf.get('mailjet_url') + path
        response = None
        try:
            with zeit.web.core.metrics.http('http') as record:
                response = method(
                    url, json=body,
                    auth=(conf['mailjet_key'], conf['mailjet_secret']),
                    timeout=conf.get('mailjet_timeout', 2))
                record(response)
            response.raise_for_status()
            return response
        except Exception:
            log.warning('%s %s failed: %s',
                        verb, url, getattr(response, 'text'), exc_info=True)
            raise
