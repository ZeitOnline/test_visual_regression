import pyramid.threadlocal
import pysolr
import requests.sessions
import zope.component

import zeit.web.core.interfaces


# Allow pysolr error handling to deal with non-ascii HTML error pages,
# see <https://bugs.python.org/issue11033>.
def scrape_response_nonascii(self, headers, response):
    if isinstance(response, str):
        response = response.decode('utf-8')
    if isinstance(response, unicode):
        response = response.encode('ascii', errors='ignore')
    return original_scrape_response(self, headers, response)
original_scrape_response = pysolr.Solr._scrape_response
pysolr.Solr._scrape_response = scrape_response_nonascii


# Make solr timeout runtime configurable
def solr_timeout_from_settings(self):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    return conf.get('solr_timeout', 5)
pysolr.Solr.timeout = property(
    solr_timeout_from_settings, lambda self, value: None)


def solr_send_request_with_referrer(self, *args, **kw):
    headers = kw.setdefault('headers', {})
    request = pyramid.threadlocal.get_current_request()
    headers['Referer'] = request.url
    headers['User-Agent'] = requests.utils.default_user_agent(
        'zeit.web-%s/pysolr/python-requests' % request.registry.settings.get(
            'version', 'unknown'))
    return original_send_request(self, *args, **kw)
original_send_request = pysolr.Solr._send_request
pysolr.Solr._send_request = solr_send_request_with_referrer


# Skip superfluous disk accesses, since we never use netrc for authentication.
requests.sessions.get_netrc_auth = lambda *args, **kw: None
