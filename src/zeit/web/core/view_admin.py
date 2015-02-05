# -*- coding: utf-8 -*-

import pyramid.view
import zeit.web.core.comments
import zope.component
import requests
import zeit.web.core.view
import pyramid.httpexceptions


def _from_localhost(context, request):
    return request.client_addr == '127.0.0.1'


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(_from_localhost,))
class PostComment(zeit.web.core.view.Base):

    def __init__(self, context, request):
        if not request.authenticated_userid:
            raise pyramid.httpexceptions.HTTPInternalServerError(
                title='No User',
                explanation='Please log in in order to comment')

        self.context = zeit.content.article.article.Article()
        self.request = request
        self.post_comment()

    def __call__(self):
        self.request.response.cache_expires(0)
        return {}

    def post_comment(self):
        request = self.request

        user = request.session['user']
        uid = user['uid']

        if request.method == 'POST':

            uniqueId = 'http://xml.zeit.de/{}'.format(
                request.params.get('path'))

            try:
                nid = zeit.web.core.comments.get_thread(
                    unique_id=uniqueId, request=request)['nid']
            except:
                raise pyramid.httpexceptions.HTTPInternalServerError(
                    title='No comment thread',
                    explanation='There was an error loading the '
                                'comment thread for {}. Please make sure the '
                                'resource and the thread exist. You can add '
                                'a thread with the helper scripts you find '
                                'in the tools directory.'.format(uniqueId))

            zwcs = zope.component.getUtility(
                zeit.web.core.interfaces.ISettings)
            action_url = '{}/agatho/thread/{}'.format(
                zwcs.get('community_host'), request.params.get('path'))
            requests.post(action_url, data={'nid': nid,
                                            'uid': uid,
                                            'comment': request.params.get(
                                                'comment'), 'pid': ''},
                          cookies=dict(request.cookies))
