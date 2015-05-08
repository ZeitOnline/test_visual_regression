# -*- coding: utf-8 -*-
import lxml
import zope.component
import pyramid.httpexceptions
import requests
import zeit.web.core
import zeit.web.core.view
import zeit.web.core.comments
import zeit.web.core.template
import pyramid.view
import urllib
import urlparse
import json


class PostComment(zeit.web.core.view.Base):
    """POST comments via http to configured community. Expects a
    request with at least a path to the resource and a comment.

    :param context, request: via pyramid view_callable
    """

    def __init__(self, context, request, path=None):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No User',
                explanation='Please log in in order to comment')
        self.cid = None
        self.action = None
        self.request_method = 'POST'
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
        cache_maker = zeit.web.core.comments.cache_maker
        request = self.request
        user = request.session['user']
        uid = user['uid']
        cid = request.params.get('cid')
        comment = request.params.get('comment')
        action = request.params.get('action')

        if not request.method == self.request_method:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Method not allowed',
                explanation=(
                    'Only {} requests are allowed for this action.'.format(
                    self.request_method)))

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
        elif action == 'report' and (not(cid) or not(comment)):
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No report could be posted',
                explanation=('comment-ID and comment needed.'))
        elif action == 'recommend' and not cid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No recommondation could be posted',
                explanation=('comment-ID needed.'))

        unique_id = 'http://xml.zeit.de/{}'.format(self.path)
        nid = self._nid_by_comment_thread(unique_id)
        action_url = self._action_url(action, self.path)

        method = 'post'
        data = {'uid': uid}
        if action == 'comment' and self.path:
            data['nid'] = nid
            data['subject'] = '[empty]'
            data['comment'] = comment
            data['pid'] = cid
        elif action == 'report' and cid:
            method = 'get'
            data['note'] = comment
            data['content_id'] = cid
            data['method'] = 'flag.flagnote'
            data['flag_name'] = 'kommentar_bedenklich'
        elif action == 'recommend' and cid:
            method = 'get'
            data['content_id'] = cid
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
                               ' (with cid {})'.format(method, unique_id, cid))

            # XXX: invalidate object from cache here!
            # use something like
            cache_maker._cache['comment_thread'].invalidate(
                (unique_id, None, None))
            # cache on other app servers should be invalidated also

            content = None
            error = None
            self.cid = cid
            if response.content:
                content = json.loads(response.content[5:-2])
                error = content['#error']
            elif response.status_code == 303:
                url = urlparse.urlparse(response.headers.get('location'))
                self.cid = url[5][4:]

            return {
                "request": {
                    "action": action,
                    "path": self.path,
                    "nid": nid,
                    "cid": cid},
                "response": {
                    "content": content,
                    "error": error,
                    "cid": self.cid}
            }

        else:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Action {} could not be performed'.format(action),
                explanation='Status code {} was send for {}'
                            'on resource {}.'.format(
                                action,
                                response.status_code,
                                unique_id))

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
            location = zeit.web.core.template.append_get_params(
                self.request, action=None, cid=None)
            if self.cid:
                location = "{}#cid-{}".format(location, self.cid)

            return pyramid.httpexceptions.HTTPSeeOther(
                location=location)


@pyramid.view.view_config(
    context='zeit.content.article.interfaces.IArticle',
    custom_predicates=(zeit.web.site.view.is_zon_content,),
    request_param='action=recommend',
    request_method='GET')
class RecommendCommentResource(PostCommentResource):
    def __init__(self, context, request):
        super(RecommendCommentResource, self).__init__(context, request)
        self.request_method = 'GET'
