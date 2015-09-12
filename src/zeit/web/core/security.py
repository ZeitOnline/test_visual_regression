import urllib2

import lxml.etree
import zope.component
import pyramid.authentication

import zeit.web.core.comments
import logging

log = logging.getLogger(__name__)


class AuthenticationPolicy(
        pyramid.authentication.SessionAuthenticationPolicy):
    """An authentication policy that queries the Community backend for user
    validation and additional user data and stores the result in the session.
    """

    def authenticated_userid(self, request):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

        # For now it is sufficient to just have an sso_cookie, because
        # zeit.web is only a proxy for the community, which will validate the
        # cookie itself.
        login_id = request.cookies.get(conf.get('sso_cookie'))


        # If no sso cookie is present, bail out straight away:
        if not login_id:
            if 'user' in request.session:
                del request.session['user']
            return

        if login_id and request.session.get('user') and (
                request.session['user'].get('sso_verification') != login_id):
            del request.session['user']

        drupal_id = None
        if request.session.get('user') and (
                request.session['user'].get('uid')):
            drupal_id = request.session['user'].get('uid')

        # If we have a community cookie for the current user, store/retrieve
        # the user info in/from the session
        if drupal_id and ('user' in request.session) and drupal_id == (
                request.session['user'].get('uid')):
            user_info = request.session['user']
        else:
            log.debug("Request user_info")
            user_info = get_community_user_info(request)
            if login_id:
                user_info['sso_verification'] = login_id
            request.session['user'] = user_info

        # Drupal 6 gives anonymous users a session and uid==0
        # in some cases they where authenticated here, but they should not be!
        if int(user_info['uid']) == 0:
            return

        return user_info['uid']


def reload_user_info(request):
        if request.authenticated_userid:
            user_info = get_community_user_info(request)
            if not user_info:
                return False
            request.session['user'] = user_info
            return True
        return False


def get_community_user_info(request):
    """Returns additional information from the Community backend by injecting
    the Cookie that Community has set when the user logged in there.
    """

    print "called"

    user_info = dict(uid=0, name=None, mail=None, picture=None, roles=[])
    community_host = request.registry.settings['community_host']

    community_request = urllib2.Request(
        community_host.rstrip('/') + '/user/xml',
        headers={'Accept': 'application/xml',
                 'Cookie': request.headers.get('Cookie', '')})

    try:
        community_response = urllib2.urlopen(community_request, timeout=6)
    except Exception:
        # Catch any possible socket error occuring through community requests.
        return user_info

    try:
        # Parse XML response and construct a dictionary from it
        xml_info = lxml.etree.fromstring(community_response.read())
    except lxml.etree.XMLSyntaxError:
        return user_info

    for key in user_info.keys():
        postfix = 'roles' in key and '/role' or ''
        elements = xml_info.xpath('/user/{}/text()'.format(key + postfix))
        if len(elements) == 0:
            continue
        elif key == 'picture':
            if elements[0] == '0':
                continue
            elements = zeit.web.core.comments.rewrite_picture_url(elements[0])
        elif 'roles' not in key:
            elements = elements[0]
        user_info[key] = elements
    return user_info
