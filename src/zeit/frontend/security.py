# -*- coding: utf-8 -*-
from pyramid.authentication import SessionAuthenticationPolicy
from webob import Request
from lxml import etree
from wsgiproxy.exactproxy import proxy_exact_request

ZMO_USER_KEY = 'zmo-user'


class AGATHOAuthenticationPolicy(SessionAuthenticationPolicy):
    """
    An authentication policy that queries the AGATHO backend for user validation
    and additional user data and stores the result in the session.
    """

    def authenticated_userid(self, request):
        # store/retrieve the user info in/from the session
        if not ZMO_USER_KEY in request.session:
            user_info = get_agatho_user_info(request)
            request.session[ZMO_USER_KEY] = user_info
        else:
            # TODO: either configure a time out or implement logout!
            user_info = request.session[ZMO_USER_KEY]

        return user_info['uid']


def get_agatho_user_info(request):
    """
    Returns additional information from the Agatho backend by injecting the Cookie
    that Agatho has set when the user logged in there.
    """
    agatho_request = Request.blank(
        'user/xml',
        base_url=request.registry.settings['agatho_host'],
        accept='application/xml')
    # inject existing Cookie
    agatho_request.headers['Cookie'] = request.headers['Cookie']
    agatho_response = agatho_request.get_response(proxy_exact_request)
    # parse XML resonse and construct a dictionary from it
    xml_info = etree.fromstring(agatho_response.body)
    user_info = dict()
    for key in ['uid', 'name', 'mail']:
        user_info[key] = xml_info.xpath('//user/%s' % key)[0].text
    return user_info
