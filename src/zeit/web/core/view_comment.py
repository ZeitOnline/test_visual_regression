# -*- coding: utf-8 -*-
import json
import urlparse
import logging

import beaker.cache
import lxml
import pyramid.httpexceptions
import pyramid.view
import requests
import zope.component

import zeit.cms.interfaces

import zeit.web.core
import zeit.web.core.comments
import zeit.web.core.template
import zeit.web.core.view


log = logging.getLogger(__name__)


class PostComment(zeit.web.core.view.Base):
    """POST comments via http to configured community. Expects a
    request with at least a path to the resource and a comment.

    :param context, request: via pyramid view_callable
    """

    def __init__(self, context, request, path=None):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPForbidden(
                title='No User',
                explanation='Please log in in order to comment')
        self.new_cid = None
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
        request = self.request
        user = request.session['user']
        uid = user['uid']
        # use submitted values for POSTs, not GET values from request url
        params = (request.GET, request.POST)[self.request_method == 'POST']
        comment = params.get('comment')
        action = params.get('action')

        try:
            pid = int(params.get('pid'))
        except (TypeError, ValueError):
            pid = None

        if not request.method == self.request_method:
            raise pyramid.httpexceptions.HTTPMethodNotAllowed(
                title='Method not allowed',
                explanation=(
                    'Only {} requests are allowed for this action.'.format(
                        self.request_method)))

        if action not in ('comment', 'report', 'recommend'):
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
        elif action == 'recommend' and not pid:
            raise pyramid.httpexceptions.HTTPBadRequest(
                title='No recommondation could be posted',
                explanation=('Pid needed.'))

        unique_id = 'http://xml.zeit.de/{}'.format(self.path)
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

        response = getattr(requests, method)(
            action_url,
            data=data,
            params=data,
            cookies=dict(request.cookies),
            allow_redirects=False)

        if response.status_code >= 200 and response.status_code <= 303:
            self.status.append('Action {} was performed for {}'
                               ' (with pid {})'.format(method, unique_id, pid))

            invalidate_comment_thread(unique_id)

            content = None
            error = None
            if response.content:
                content = json.loads(response.content[5:-2])
                error = content['#error']
            elif response.status_code == 303:
                url = urlparse.urlparse(response.headers.get('location'))
                self.new_cid = url[5][4:]

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
                    'new_cid': self.new_cid}
            }

        else:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Action {} could not be performed'.format(action),
                explanation='Status code {} was send for action {} '
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

    def _get_recommendations(self, unique_id, pid):
        comment_thread = zeit.web.core.comments.get_cacheable_thread(unique_id)

        if comment_thread and comment_thread['index'][pid]:
            comment = comment_thread['index'][pid]
            if len(comment['fans']):
                return comment['fans'].split(',')

        return []

    def _nid_by_comment_thread(self, unique_id):
        # Needed to prevent 'UnboundLocalError' in 'if not nid'
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

        # invalidate comment thread to get the newly created comment section ID
        # only the thread of the current app server gets invalidated here
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
                self.request, action=None, pid=None, cid=self.new_cid)
            if self.new_cid:
                # remove page param in redirect
                location = zeit.web.core.template.remove_get_params(
                    location, 'page')
                location = '{}#cid-{}'.format(location, self.new_cid)
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
class RecommendCommentResource(PostCommentResource):
    def __init__(self, context, request):
        super(RecommendCommentResource, self).__init__(context, request)
        self.request_method = 'GET'


def invalidate_comment_thread(unique_id):
    beaker.cache.region_invalidate(
        zeit.web.core.comments.get_cacheable_thread,
        None,
        'comment_thread',
        unique_id)
