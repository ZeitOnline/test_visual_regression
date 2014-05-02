# -*- coding: utf-8 -*-
from pyramid.authentication import SessionAuthenticationPolicy
from webob import Request
from lxml import etree
from wsgiproxy.exactproxy import proxy_exact_request

ZMO_USER_KEY = 'zmo-user'


class CommunityAuthenticationPolicy(SessionAuthenticationPolicy):
    """
    An authentication policy that queries the Community backend for user validation
    and additional user data and stores the result in the session.
    """

    def authenticated_userid(self, request):
        drupal_id = request.cookies.get('drupal-userid')
        # if no community cookie is present, bail out straight away:
        if drupal_id is None:
            # avoid stale session data by making sure it's deleted
            if ZMO_USER_KEY in request.session:
                del request.session[ZMO_USER_KEY]
            return None
 
        # if we have a community cookie for the current user, store/retrieve the user info in/from the session
        if ZMO_USER_KEY in request.session and drupal_id == request.session[ZMO_USER_KEY].get('uid'):
            user_info = request.session[ZMO_USER_KEY]
        else:
            user_info = get_community_user_info(request)
            request.session[ZMO_USER_KEY] = user_info

        return user_info['uid']


def get_community_user_info(request):
    """
    Returns additional information from the Community backend by injecting the Cookie
    that Community has set when the user logged in there.
    """
    community_request = Request.blank(
        'user/xml',
        base_url=request.registry.settings['community_host'],
        accept='application/xml')
    # inject existing Cookie
    community_request.headers['Cookie'] = request.headers['Cookie']
    community_response = community_request.get_response(proxy_exact_request)
    # parse XML resonse and construct a dictionary from it
    xml_info = etree.fromstring(community_response.body)
    user_info = dict()
    for key in ['uid', 'name', 'picture']:
        user_info[key] = xml_info.xpath('//user/%s' % key)[0].text
    return user_info
