import urllib2
import jwt

import lxml.etree
import zope.component
import pyramid.authentication

import zeit.web.core.comments
import zeit.web.core.metrics
import logging

log = logging.getLogger(__name__)


class AuthenticationPolicy(
        pyramid.authentication.SessionAuthenticationPolicy):
    """An authentication policy that queries the Community backend for user
    validation and additional user data and stores the result in the session.
    """

    def authenticated_userid(self, request):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

        login_id = request.cookies.get(conf.get('sso_cookie'))

        # If no sso cookie is present, bail out straight away:
        if not login_id:
            if 'user' in request.session:
                del request.session['user']
            return

        # Make sure sso_verification in the user session matches the one send
        # via request
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


def get_user_info_from_sso_cookie(cookie, key):
    try:
        return jwt.decode(cookie, key, 'RS256')
    except Exception:
        return


def recursively_call_community(req, tries):
    if tries > 0:
        try:
            with zeit.web.core.metrics.timer(
                    'community_user_info.community.reponse_time'):
                return urllib2.urlopen(req, timeout=2)
        except Exception:
            return recursively_call_community(req, tries - 1)
    else:
        return


def get_community_user_info(request):
    """Returns additional information from the Community backend by injecting
    the Cookie that Community has set when the user logged in there.
    """

    user_info = dict(uid=0, name=None, mail=None, picture=None, roles=[])

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    cookie = request.cookies.get(conf.get('sso_cookie'))
    sso_info = get_user_info_from_sso_cookie(cookie, conf.get('sso_key'))

    if sso_info:
        user_info['name'] = sso_info.get('name')
        user_info['mail'] = sso_info.get('email')
        user_info['uid'] = sso_info['id']

    # We still get the users avatar from the community. So we need to call the
    # community.
    community_host = request.registry.settings['community_host']

    community_request = urllib2.Request(
        community_host.rstrip('/') + '/user/xml',
        headers={'Accept': 'application/xml',
                 'Cookie': request.headers.get('Cookie', '')})

    community_response = recursively_call_community(community_request, 1)

    if not community_response:
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

    if len(user_info.get('roles', [])) == 1:
        roles = user_info['roles'][:]
        user_info['blocked'] = (roles.pop() == "anonymous user")
    return user_info
