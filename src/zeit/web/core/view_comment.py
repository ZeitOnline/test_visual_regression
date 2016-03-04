# -*- coding: utf-8 -*-
import json
import logging
import md5
import urllib
import urlparse
import datetime

import lxml
import pyramid.httpexceptions
import pyramid.view
import requests
import requests.exceptions
import zope.component

import zeit.cms.interfaces

import zeit.web.core
import zeit.web.core.comments
import zeit.web.core.metrics
import zeit.web.core.security
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.site.view


log = logging.getLogger(__name__)


class PostComment(zeit.web.core.view.Base):
    """POST comments via http to configured community. Expects a
    request with at least a path to the resource and a comment.

    :param context, request: via pyramid view_callable
    """

    def __init__(self, context, request, path=None):

        if not request.user:
            raise pyramid.httpexceptions.HTTPForbidden(
                title='No User',
                explanation='Please log in in order to comment')

        if not request.user.get('name'):
            self.user_name = ''
        else:
            self.user_name = request.user['name']

        self.new_cid = None
        self.request_method = 'POST'
        self.path = request.params.get('path') or path
        self.context = context
        self.request = request
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.community_host = zwcs.get('community_host')
        self.status = []
        self.lock_duration = datetime.timedelta(0, 20)

    def __call__(self):
        self.request.response.cache_expires(0)
        return {}

    def handle_comment_locking(self, request, action):
        if action in ('recommend', 'promote', 'demote'):
            return

        if request.session.get('lock_commenting'):
            ts = request.session['lock_commenting_ts']
            if datetime.datetime.utcnow() - ts > self.lock_duration:
                log.debug("remove comment lock!")
                request.session['lock_commenting'] = False
                request.session['lock_commenting_ts'] = (
                    datetime.datetime.utcnow())
            else:
                log.debug("commenting is locked!")
                raise pyramid.httpexceptions.HTTPForbidden()

        log.debug("set comment lock!")
        request.session['lock_commenting'] = True
        request.session['lock_commenting_ts'] = datetime.datetime.utcnow()

    def post_comment(self):
        request = self.request
        # XXX We should not have to transmit this; Community can get it itself
        # from the SSO cookie.
        uid = request.user['uid']
        # use submitted values for POSTs, not GET values from request url
        params = (request.GET, request.POST)[self.request_method == 'POST']
        comment = params.get('comment')
        action = params.get('action')
        user_name = params.get('username')
        unique_id = 'http://xml.zeit.de/{}'.format(self.path)

        self.handle_comment_locking(request, action)

        try:
            pid = int(params.get('pid'))
        except (TypeError, ValueError):
            pid = None

        if not user_name and not self.user_name and action == 'comment':
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='No user_name given',
                explanation='A user name must be set in order to comment.')

        if not self.user_name and user_name and not action == 'comment':
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='A user_name could not be set',
                explanation='A user name can only be set on action comment.')

        if not request.method == self.request_method:
            raise pyramid.httpexceptions.HTTPMethodNotAllowed(
                title='Method not allowed',
                explanation=(
                    'Only {} requests are allowed for this action.'.format(
                        self.request_method)))

        if action not in (
                'comment', 'report', 'recommend', 'promote', 'demote'):
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='Nothing could be posted',
                explanation=(
                    'Action is not set or not allowed. '
                    'Choose one of comment, recommend or report.'))

        if not self.path:
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='Nothing could be posted',
                explanation=(
                    'We need a resource path '
                    'in order to load a comment thread.'))

        if action == 'comment' and not comment:
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='No comment could be posted',
                explanation=('Path and comment needed.'))
        elif action == 'report' and (not(pid) or not(comment)):
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='No report could be posted',
                explanation=('Pid and comment needed.'))
        elif action == 'recommend':
            if not pid:
                raise pyramid.httpexceptions.HTTPBadRequest(
                    title='No recommondation could be posted',
                    explanation=('Pid needed.'))
            commenter = self._get_commenter_id(unique_id, pid)
            if commenter == uid:
                raise pyramid.httpexceptions.HTTPBadRequest(
                    title='No recommondation could be posted',
                    explanation=('Own comments must not be recommended.'))

        nid = self._nid_by_comment_thread(unique_id)
        action_url = self._action_url(action, self.path)

        method = 'post'
        data = {'uid': uid}
        recommendations = None
        if action == 'comment' and self.path:
            data['nid'] = nid
            data['subject'] = '[empty]'
            data['comment'] = comment
            data['pid'] = pid
            if not self.user_name:
                data['user_name'] = user_name

        elif action == 'report' and pid:
            method = 'get'
            data['note'] = comment
            data['content_id'] = pid
            data['method'] = 'flag.flagnote'
            data['flag_name'] = 'kommentar_bedenklich'
        elif action == 'recommend' and pid:
            fans = self._get_recommendations(unique_id, pid)
            if uid in fans:
                data['action'] = 'unflag'
                fans.remove(uid)
            else:
                data['action'] = 'flag'
                fans.append(uid)
            recommendations = len(fans)
            method = 'get'
            data['content_id'] = pid
            data['method'] = 'flag.flag'
            data['flag_name'] = 'leser_empfehlung'
        elif action in ('promote', 'demote') and pid:
            method = 'get'
            data['content_id'] = pid
            data['method'] = 'flag.flag'
            data['flag_name'] = 'kommentar_empfohlen'
            if action == 'demote':
                data['action'] = 'unflag'

        # GET/POST the request to the community
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        with zeit.web.core.metrics.timer(
                'post_comment.community.reponse_time'):
            try:
                response = getattr(requests, method)(
                    action_url,
                    data=data,
                    params=data,
                    cookies=dict(request.cookies),
                    allow_redirects=False,
                    timeout=float(conf.get('community_host_timeout_secs', 5)))
                if not 200 <= response.status_code <= 303:
                    raise requests.exceptions.HTTPError()
            except requests.exceptions.HTTPError as err:
                if response.status_code == 409:
                    try:
                        detail = json.loads(response.content)['error_message']
                    except (AttributeError, KeyError, ValueError):
                        detail = u''
                    message = u'user_name could not be set'
                    log.warning(message + u' ' + detail)
                    raise pyramid.httpexceptions.HTTPBadRequest(
                        title=message, explanation=detail)
                else:
                    message = u'Action {} could not be performed'.format(
                        action)
                    detail = (u'Status code {} was sent for action {} '
                              u'on resource {}'.format(
                                  response.status_code, action, unique_id))
                    log.warning(message + u' ' + detail)
                    raise pyramid.httpexceptions.HTTPInternalServerError(
                        title=message, explanation=detail)
            except requests.exceptions.RequestException as err:
                message = u'Action {} could not be performed'.format(action)
                detail = u'{} was raised for action {} on resource {}'.format(
                    type(err).__name__, action, unique_id)
                log.warning(message + u' ' + detail)
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title=message, explanation=detail)

        self.status.append('Action {} was performed for {}'
                           ' (with pid {})'.format(method, unique_id, pid))
        invalidate_comment_thread(unique_id)
        set_user = False
        if not self.user_name and action == 'comment':
            zeit.web.core.security.reload_user_info(request)
            if request.user.get('name'):
                self.user_name = request.user['name']
                set_user = True
                self.status.append(u"User name {} was set".format(
                    self.user_name))
            else:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No user name found',
                    explanation='Session could not be '
                                'reloaded with new user_name.')

        content = None
        error = None
        if response.content:
            content = json.loads(response.content[5:-2])
            error = content['#error']
        elif response.status_code == 303:
            url = urlparse.urlparse(response.headers.get('location'))
            self.new_cid = url[5][4:]
            request.session['last_cid'] = self.new_cid
            request.session['last_commented_uniqueId'] = (
                self.context.uniqueId)
            request.session['last_commented_time'] = (
                datetime.datetime.utcnow())

        premoderation = True if (response.status_code == 202 and (
            response.headers.get('x-premoderation') == 'true')) else False

        if premoderation:
            self.status.append(
                'Comment needs moderation (premoderation state)')

        return {
            'request': {
                'action': action,
                'path': self.path,
                'nid': nid,
                'pid': pid},
            'response': {
                'content': content,
                'error': error,
                'recommendations': recommendations,
                'new_cid': self.new_cid,
                'setUser': set_user,
                'userName': self.user_name,
                'premoderation': premoderation}}

    def _action_url(self, action, path):
        endpoint = 'services/json?callback=zeit' if (action in [
            'promote', 'demote', 'recommend', 'report']) else 'agatho/thread'

        if endpoint == 'services/json?callback=zeit':
            path = ''

        return '{}/{}/{}'.format(
            self.community_host, endpoint, path).strip('/')

    def _get_recommendations(self, unique_id, pid):
        comment_thread = zeit.web.core.comments.get_cacheable_thread(unique_id)

        if comment_thread and comment_thread.get('index', {}).get(pid):
            comment = comment_thread['index'][pid]
            if len(comment['fans']):
                return comment['fans'].split(',')

        return []

    def _get_commenter_id(self, unique_id, pid):
        comment_thread = zeit.web.core.comments.get_cacheable_thread(unique_id)

        if comment_thread and comment_thread.get('index', {}).get(pid):
            return comment_thread['index'][pid]['uid']

    def _nid_by_comment_thread(self, unique_id):
        nid = None
        comment_thread = zeit.web.core.comments.get_cacheable_thread(unique_id)

        if comment_thread:
            return comment_thread.get('nid')
        else:
            comment_thread = self._create_and_load_comment_thread(unique_id)

            if comment_thread:
                nid = comment_thread.get('nid')

        if not nid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No comment thread',
                explanation=('No comment thread for {} could be '
                             'created.').format(unique_id))
        return nid

    def _create_and_load_comment_thread(self, unique_id):
        content = None
        try:
            content = zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Resource does not exist',
                explanation='The resource {} does not exist and there is'
                            'no comment_thread for it.'.format(unique_id))

        xml_str = lxml.etree.tostring(content.xml)
        headers = {
            'X-uniqueId': '{}{}'.format(
                self.request.route_url('home').rstrip('/'),
                urlparse.urlparse(unique_id)[2]),
            'Content-Type': 'text/xml'}

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        with zeit.web.core.metrics.timer(
                'create_thread.community.reponse_time'):
            response = requests.post(
                '{}/agatho/commentsection'.format(self.community_host),
                headers=headers,
                data=xml_str,
                timeout=float(conf.get('community_host_timeout_secs', 5)))

        if not response.status_code >= 200 and not response.status_code < 300:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Comment Section could not be created',
                explanation='The comment section for the resource {} '
                            'could not be created'.format(unique_id))

        self.status.append('A comment section for {} was created'.format(
            unique_id))

        # invalidate comment thread to get the newly created comment section ID
        invalidate_comment_thread(unique_id)

        return zeit.web.core.comments.get_cacheable_thread(unique_id)


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(zeit.web.core.is_admin,))
class PostCommentAdmin(PostComment):
    def __init__(self, context, request):
        super(PostCommentAdmin, self).__init__(context, request)
        self.context = zeit.content.article.article.Article()

        if request.method == 'POST':
            self.post_comment()


@pyramid.view.view_defaults(renderer='json', request_method='POST')
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle,
                          name='komplettansicht')
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle,
                          name='seite')
@pyramid.view.view_config(context=zeit.web.core.gallery.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
@pyramid.view.view_config(context=zeit.web.core.article.ILiveblogArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IShortformArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IColumnArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
class PostCommentResource(PostComment):

    msg = {'Username exists or not valid': 'username_exists_or_invalid'}

    def __init__(self, context, request):
        super(PostCommentResource, self).__init__(context, request)
        self.path = urlparse.urlparse(self.context.uniqueId)[2][1:]

    def __call__(self):
        self.request.response.cache_expires(0)
        result = {}
        try:
            result = self.post_comment()
        except pyramid.httpexceptions.HTTPBadRequest, e:
            result = {'error': self.msg.get(unicode(e))}
            params = self.request.params
            action = params.get('action')
            if action == 'comment':
                result['comment'] = params.get('comment')
                result['pid'] = params.get('pid')
                result['user_name'] = params.get('username')

        location = zeit.web.core.template.append_get_params(
            self.request,
            action=None,
            pid=None,
            cid=self.new_cid)

        location = zeit.web.core.template.remove_get_params(location, 'ajax')

        if self.new_cid:
            # remove page param in redirect
            location = zeit.web.core.template.remove_get_params(
                location, 'page')
            location = '{}#cid-{}'.format(location, self.new_cid)

        if self.request.params.get('ajax') == 'true':
            result['location'] = location
            return result

        # We might need to save data to our user session, because
        # we want to perform a redirect after a POST, but we want to
        # have the actual data available, which might be to long for
        # GET params.
        if 'error' in result:
            md5sum = md5.md5(json.dumps(result, sort_keys=True)).hexdigest()
            self.request.session[md5sum] = result
            location = zeit.web.core.template.append_get_params(
                self.request,
                action=None,
                error=md5sum)
            location = '{}#comment-form'.format(location)

        return pyramid.httpexceptions.HTTPSeeOther(location=location)


@pyramid.view.view_defaults(
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_param='action=recommend',
    request_method='GET')
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle,
                          name='komplettansicht')
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle,
                          name='seite')
@pyramid.view.view_config(context=zeit.web.core.gallery.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
@pyramid.view.view_config(context=zeit.web.core.article.ILiveblogArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IShortformArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IColumnArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
class RecommendCommentResource(PostCommentResource):
    def __init__(self, context, request):
        # redirect unauthorized recommendation request
        # prevent 403 HTTPForbidden response in PostComment
        if not request.user:
            if request.registry.settings.sso_activate:
                pattern = '{}/anmelden?url={}'
                host = request.registry.settings.get('sso_url')
            else:
                pattern = '{}/user/login?destination={}'
                host = request.registry.settings.get('community_host')

            location = pattern.format(host, urllib.quote_plus(request.url))
            raise pyramid.httpexceptions.HTTPSeeOther(location=location)

        super(RecommendCommentResource, self).__init__(context, request)
        self.request_method = 'GET'


def invalidate_comment_thread(unique_id):
    zeit.web.core.comments.get_cacheable_thread.invalidate(unique_id)


@pyramid.view.view_config(route_name='invalidate_comment_thread')
def invalidate(request):
    if not request.headers.get('X-Watchword', None) == 'g@ldf1nch':
        raise pyramid.httpexceptions.HTTPForbidden(
            title='Wrong password',
            explanation='Use correct password to work with me.')

    path = request.params.get('path', None)
    unique_id = 'http://xml.zeit.de/{}'.format(path)

    if not path:
        raise pyramid.httpexceptions.HTTPBadRequest(
            title='No path given',
            explanation='A path must be set in order to make me happy.')

    try:
        if unique_id and zeit.cms.interfaces.ICMSContent(unique_id):
            invalidate_comment_thread(unique_id)
            return pyramid.response.Response('OK', 200)
    except TypeError, err:
        raise pyramid.httpexceptions.HTTPBadRequest(
            title='Type error',
            explanation='Error: {}'.format(err))


@pyramid.view.view_config(route_name='invalidate_community_maintenance')
def invalidate_maintenance(request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    unique_id = conf.get('community_maintenance')
    if not unique_id:
        raise pyramid.httpexceptions.HTTPBadRequest(
            title='No path given',
            explanation='A maintenance object is not configured.')

    zeit.web.core.comments._community_maintenance_cache.invalidate(unique_id)
    return pyramid.response.Response('OK', 200)
