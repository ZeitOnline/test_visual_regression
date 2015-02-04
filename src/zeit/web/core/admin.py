# -*- coding: utf-8 -*-

import pyramid.view
import zeit.web.core.comments
import zope.component
import requests

def _from_localhost(context, request):
    return request.client_addr == '127.0.0.1'


@pyramid.view.view_config(route_name='post_test_comments',
                          renderer='templates/post_test_comments.html',
                          custom_predicates=(_from_localhost,))
def post_comments(request):
    if request.method == 'POST':
        user = request.session['user']
        uid = user['uid']
        uniqueId = 'http://xml.zeit.de/{}'.format(request.params.get('path'))

        nid = zeit.web.core.comments.get_thread(
                unique_id=uniqueId, request=request)

        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        action_url = '{}/agatho/thread/{}'.format(zwcs.get('community_host'),
                                                  request.params.get('path'))

        result = requests.post(action_url, params={'nid': nid,
            'uid': uid, 'comment': request.params.get('comment')},
            cookies=request.cookies)

        import pdb; pdb.set_trace()  # XXX BREAKPOINT


    return {}
