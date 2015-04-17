# -*- coding: utf-8 -*-

import pyramid.view
import zeit.web.core.comments
import zope.component
import requests
import zeit.web.core.view
import pyramid.httpexceptions
import lxml.etree
import urlparse


def _is_admin(context, request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if conf.get('is_admin'):
        return True
    return request.client_addr == '127.0.0.1'


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(_is_admin,))
class PostComment(zeit.web.core.view.Base):

    def __init__(self, context, request):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No User',
                explanation='Please log in in order to comment')

        self.context = zeit.content.article.article.Article()
        self.request = request
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.community_host = zwcs.get('community_host')
        self.status = []
        self.post_comment()

    def __call__(self):
        self.request.response.cache_expires(0)
        return {}

    def post_comment(self):
        request = self.request

        user = request.session['user']
        uid = user['uid']

        if request.method == 'POST':

            unique_id = 'http://xml.zeit.de/{}'.format(
                request.params.get('path'))

            comment_thread = zeit.web.core.comments.get_thread(
                unique_id, destination=request.url)
            nid = None
            if comment_thread:
                nid = comment_thread['nid']
            else:
                nid = self._create_and_load_comment_thread(unique_id)['nid']
            if not nid:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No comment thread',
                    explanation='No comment thread for {} could be '
                                'created.'.format(unique_id))

            action_url = '{}/agatho/thread/{}'.format(
                self.community_host, request.params.get('path'))

            data = {'nid': nid,
                    'uid': uid,
                    'subject': '[empty]',
                    'comment': request.params.get('comment'),
                    'pid': request.params.get('pid')}
            response = requests.post(action_url, data=data,
                                     cookies=dict(request.cookies))

            if response.status_code == 200:
                self.status.append('A comment for {} was posted'.format(
                    unique_id))
            else:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No comment could be posted',
                    explanation='No comment  for {} could be '
                                'posted.'.format(unique_id))

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

        if not response.status_code == 204:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='Comment Section could not be created',
                explanation='The comment section for the resource {} '
                            'could not be created'.format(unique_id))

        self.status.append('A comment section for {} was created'.format(
            unique_id))

        return zeit.web.core.comments.get_thread(
            unique_id, destination=self.request.url)
