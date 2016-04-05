import jwt
import requests
import lxml.etree
import zope.component
import pyramid.authentication

import zeit.web.core.comments
import zeit.web.core.metrics
import logging


log = logging.getLogger(__name__)


class AuthenticationPolicy(
        pyramid.authentication.SessionAuthenticationPolicy):
    """An authentication policy that reads and validates the SSO cookie,
    queries the Community backend for user validation and additional user data
    and stores the result in the session.
    """

    def authenticated_userid(self, request):
        return request.user.get('ssoid')


def get_user(request):
    """This is available as ``request.user``."""
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    sso_cookie = request.cookies.get(conf.get('sso_cookie'))
    if not sso_cookie:
        if 'user' in request.session:
            del request.session['user']
        return {}

    stored_user = request.session.get('user', {})
    if (not is_reliable_user_info(stored_user) or
            stored_user.get('should_invalidate')):
        log.debug('No user found in session, calling get_user_info()')
        user_info = get_user_info(request)
        if not is_reliable_user_info(user_info):
            return {}
        request.session['user'] = user_info
        return user_info
    else:
        return stored_user


def is_reliable_user_info(user_info):
    """Check user info for all mandatory session values (including the
    successfully decoded SSO cookie value).
    """
    ssoid = user_info.get('ssoid')
    if ssoid and not user_info.get('has_community_data'):
        user_info['should_invalidate'] = True
    return bool(ssoid)


def reload_user_info(request):
    if request.session.get('user'):
        del request.session['user']
        del request.user
    return request.user


def get_user_info(request):
    """Returns additional information from the Community backend by injecting
    the Cookie that Community has set when the user logged in there.
    """

    user_info = dict(
        uid=0,
        name=None,
        mail=None,
        should_invalidate=False,
        has_community_data=False,
        picture=None,
        roles=[],
        premoderation=False)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    cookie = request.cookies.get(conf.get('sso_cookie'))
    sso_info = get_user_info_from_sso_cookie(cookie, conf.get('sso_key'))

    if sso_info:
        user_info['name'] = sso_info.get('name')
        user_info['mail'] = sso_info.get('email')
        user_info['ssoid'] = sso_info['id']
        user_info['sso_verification'] = cookie

    # We still get the users avatar from the community. So we need to call the
    # community.
    community_host = request.registry.settings['community_host']

    community_request = requests.Request(
        'GET', community_host.rstrip('/') + '/user/xml',
        headers={'Accept': 'application/xml',
                 'Cookie': request.headers.get('Cookie', '')}).prepare()

    community_response = _retry_request(community_request, 1)

    if not community_response:
        return user_info

    try:
        # Parse XML response and construct a dictionary from it
        xml_info = lxml.etree.parse(community_response.raw)
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
        elif key == 'premoderation':
            elements = True if int(elements[0]) else False
        elif 'roles' not in key:
            elements = elements[0]
        user_info[key] = elements

    if len(user_info.get('roles', [])) == 1:
        roles = user_info['roles'][:]
        user_info['blocked'] = (roles.pop() == "anonymous user")

    user_info['has_community_data'] = True
    return user_info


def get_user_info_from_sso_cookie(cookie, key):
    try:
        return jwt.decode(cookie, key, 'RS256')
    except Exception:
        return


def _retry_request(request, tries):
    if not tries:
        return
    try:
        with zeit.web.core.metrics.timer(
                'community_user_info.community.reponse_time'):
            # Analoguous to requests.api.request().
            session = requests.Session()
            response = session.send(request, stream=True, timeout=0.5)
            session.close()
            return response
    except Exception:
        return _retry_request(request, tries - 1)


def get_login_state(request):
    settings = request.registry.settings
    destination = request.params['context-uri'] if request.params.get(
        'context-uri') else request.route_url('home').rstrip('/')
    info = {}

    if not request.authenticated_userid and request.cookies.get(
            settings.get('sso_cookie')):
        log.warn('SSO Cookie present, but not authenticated')

    info['login'] = u'{}/anmelden?url={}'.format(
        settings['sso_url'], destination)
    info['logout'] = u'{}/abmelden?url={}'.format(
        settings['sso_url'], destination)

    if request.user:
        info['user'] = request.user
        info['profile'] = "{}/user".format(settings['community_host'])
    return info
