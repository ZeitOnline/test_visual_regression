# -*- coding: utf-8 -*-
import lxml
import zope.component
import pyramid.httpexceptions
import requests
import zeit.web.core
import zeit.web.core.view
import zeit.web.core.comments
import pyramid.view
import urlparse
import json
import logging

import zeit.cms.interfaces

log = logging.getLogger(__name__)


class PostComment(zeit.web.core.view.Base):
    """POST comments via http to configured community. Expects a
    request with at least a path to the resource or the nid in drupal and
    a comment.

    :param context, request: via pyramid view_callable
    """

    def __init__(self, context, request, path=None):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No User',
                explanation='Please log in in order to comment')
        self.pid = None
        self.action = None
        self.path = request.params.get('path') or path
        self.context = context
        self.request = request
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.community_host = zwcs.get('community_host')
        self.status = []

    def __call__(self):
        self.request.response.cache_expires(0)
        return {}

    def post_comment(self):
        request = self.request
        user = request.session['user']
        uid = user['uid']
        pid = request.params.get('pid')
        comment = request.params.get('comment')
        action = request.params.get('action')

        if not request.method == "POST":
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title="No comment could be posted",
                explanation="Only post request are allowed")

        if action not in ('comment', 'report', 'recommend'):
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Nothing could be posted',
                explanation=(
                    'Action is not set or not allowed. '
                    'Choose one of comment, recommend or report.'))

        if not self.path:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Nothing could be posted',
                explanation=(
                    'We need a resource path '
                    'in order to load a comment thread.'))

        if action == 'comment' and not comment:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No comment could be posted',
                explanation=('Path and comment needed.'))
        elif action == 'report' and (not(pid) or not(comment)):
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No report could be posted',
                explanation=('Pid and comment needed.'))
        elif action == 'recommend' and not pid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No recommondation could be posted',
                explanation=('Pid needed.'))

        unique_id = 'http://xml.zeit.de/{}'.format(self.path)
        nid = self._nid_by_comment_thread(unique_id)
        action_url = self._action_url(action, self.path)

        method = 'post'
        data = {'uid': uid}
        if action == 'comment' and self.path:
            data['nid'] = nid
            data['subject'] = '[empty]'
            data['comment'] = comment
            data['pid'] = pid
        elif action == 'report' and pid:
            method = 'get'
            data['note'] = comment
            data['content_id'] = pid
            data['method'] = 'flag.flagnote'
            data['flag_name'] = 'kommentar_bedenklich'
        elif action == 'recommend' and pid:
            method = 'get'
            data['content_id'] = pid
            data['method'] = 'flag.flag'
            data['flag_name'] = 'leser_empfehlung'

        response = getattr(requests, method)(
            action_url,
            data=data,
            params=data,
            cookies=dict(request.cookies),
            allow_redirects=False)

        if response.status_code >= 200 and response.status_code <= 303:
            self.status.append('Action {} was performed for {}'
                               ' (with pid {})'.format(method, unique_id, pid))

            self._invalidate_app_servers(unique_id)

            content = None
            new_content_id = None
            if response.content:
                content = json.loads(response.content[5:-2])
            elif response.status_code == 303:
                url = urlparse.urlparse(response.headers.get('location'))
                new_content_id = url[5][4:]

            return {
                "request": {
                    "action": action,
                    "path": self.path,
                    "nid": nid,
                    "pid": pid},
                "response": {
                    "content": content,
                    "new_content_id": new_content_id}
            }

        else:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Action {} could not be performed'.format(action),
                explanation='Status code {} was send for {}'
                            'on resource {}.'.format(
                                action,
                                response.status_code,
                                unique_id))

    def _invalidate_app_servers(self, unique_id):
        # We can save ourself a request, if we don't invalidate the current
        # app via http.
        invalidate_comment_thread(unique_id)
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        servers = conf.get('app_servers', None)
        import pdb; pdb.set_trace()  # XXX BREAKPOINT

        if not servers:
            return

        for server in servers:
            url = '{}/json/invalidate?unique_id={}'.format(
                server,
                unique_id)

            try:
                requests.get(url)
            except:
                log.warning('{} could not be invalidated on {}'.format(
                    unique_id,
                    server))

    def _action_url(self, action, path):
        endpoint = 'services/json?callback=zeit' if (
            action in ['recommend', 'report']) else 'agatho/thread'

        if endpoint == 'services/json?callback=zeit':
            path = ''

        return '{}/{}/{}'.format(
            self.community_host, endpoint, path).strip('/')

    def _nid_by_comment_thread(self, unique_id):
        comment_thread = zeit.web.core.comments.get_thread(unique_id)

        if comment_thread:
            return comment_thread.get('nid')

        nid = self._create_and_load_comment_thread(unique_id).get('nid')
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
            'X-uniqueId': 'http://{}{}'.format(
                self.request.host, urlparse.urlparse(unique_id)[2]),
            'Content-Type': 'text/xml'}
        response = requests.post(
            '{}/agatho/commentsection'.format(self.community_host),
            headers=headers,
            data=xml_str)

        if not response.status_code >= 200 and not response.status_code < 300:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Comment Section could not be created',
                explanation='The comment section for the resource {} '
                            'could not be created'.format(unique_id))

        self.status.append('A comment section for {} was created'.format(
            unique_id))

        return zeit.web.core.comments.get_thread(
            unique_id, destination=self.request.url)


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(zeit.web.core.is_admin,))
class PostCommentAdmin(PostComment):
    def __init__(self, context, request):
        super(PostCommentAdmin, self).__init__(context, request)
        self.context = zeit.content.article.article.Article()

        if request.method == "POST":
            self.post_comment()


@pyramid.view.view_config(
    context='zeit.content.article.interfaces.IArticle',
    renderer='json',
    request_method='POST')
class PostCommentResource(PostComment):
    def __init__(self, context, request):
        super(PostCommentResource, self).__init__(context, request)
        self.path = urlparse.urlparse(self.context.uniqueId)[2][1:]

    def __call__(self):
        self.request.response.cache_expires(0)
        result = self.post_comment()

        if self.request.params.get('ajax') == 'true':
            return result
        else:
            location = self.request.url
            if self.pid:
                location = "{}#cid-{}".format(location, self.pid)

            return pyramid.httpexceptions.HTTPSeeOther(
                location=location)


@pyramid.view.view_config(
    route_name='json_invalidate',
    renderer='json')
def invalidate(request):
    unique_id = request.params.get('unique_id', None)
    if not unique_id:
        raise pyramid.httpexceptions.HTTPInternalServerError(
            title='No unique_id given')

    url = urlparse.urlparse(unique_id)
    if not url.scheme:
        raise pyramid.httpexceptions.HTTPInternalServerError(
            title='unique_id is not a valid url')

    try:
        zeit.cms.interfaces.ICMSContent(unique_id)
    except TypeError:
        raise pyramid.httpexceptions.HTTPInternalServerError(
            title='unique_id does not exist')

    invalidate_comment_thread(unique_id)
    return {"msg": "{} was invalidated".format(unique_id)}


def invalidate_comment_thread(unique_id):
    cache_maker = zeit.web.core.comments.cache_maker
    cache_maker._cache['comment_thread'].invalidate((unique_id,))
