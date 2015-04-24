# -*- coding: utf-8 -*-
import lxml
import zope.component
import pyramid.httpexceptions
import requests
import zeit.web.core.view
import zeit.web.core.comments
import pyramid.view
import urlparse


def _is_admin(context, request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if conf.get('is_admin'):
        return True
    return request.client_addr == '127.0.0.1'


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

        if request.method == "POST":
            if (not self.path or not request.params.get('comment')):
                    raise pyramid.httpexceptions.HTTPInternalServerError(
                        title='No comment could be posted',
                        explanation=('Path and comment are required'))

            unique_id = 'http://xml.zeit.de/{}'.format(self.path)
            nid = self._nid_by_comment_thread(unique_id)

            action_url = _action_url(request, self.path)

            data = {'nid': nid,
                    'uid': uid,
                    'subject': '[empty]',
                    'comment': request.params.get('comment'),
                    'pid': request.params.get('pid')}
            response = requests.post(action_url, data=data,
                                     cookies=dict(request.cookies))

            if response.status_code >= 200 and response.status_code < 300:
                self.status.append('A comment for {} was posted'.format(
                    unique_id))
                # XXX: invalidate object from cache here!
                # use something like
                cache_maker._cache['comment_thread'].invalidate(
                    (unique_id, None, None))
                # cache on other app servers should be invalidated also
            else:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No comment could be posted',
                    explanation='No comment  for {} could be '
                                'posted.'.format(unique_id))

    def _action_url(self, request, path):
        endpoint = 'services/json' if (
            request.params.get('is_questionable')) else 'agatho/thread'

        if endpoint == 'services/json':
            path = ''

        return '{}/{}/{}'.format(
            self.community_host, endpoint, path)

    def _nid_by_comment_thread(self, unique_id):
        comment_thread = zeit.web.core.comments.get_thread(unique_id)

        if comment_thread:
            return comment_thread['nid']

        nid = self._create_and_load_comment_thread(unique_id)['nid']
        if not nid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No comment thread',
                explanation=('No comment thread for {} could be '
                             'created.').format(unique_id))
        else:
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
                          custom_predicates=(_is_admin,))
class PostCommentAdmin(PostComment):
    def __init__(self, context, request):
        super(PostCommentAdmin, self).__init__(context, request)
        self.context = zeit.content.article.article.Article()
        self.post_comment()
