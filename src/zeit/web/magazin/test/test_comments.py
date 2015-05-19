# -*- coding: utf-8 -*-
import mock
import urlparse

import zeit.cms.interfaces


def test_comment_post_url_contains_destination(application, testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    request = mock.Mock()
    request.url = 'foo.bar/artikel/01'
    view = zeit.web.magazin.view_article.Article(context, request)
    url = view.comments.get('comment_post_url')
    scheme, netloc, path, query, frag = urlparse.urlsplit(url)
    param = urlparse.parse_qs(query, True)

    assert param.get('destination') == [request.url]


def test_comment_thread_contains_comment_report_url(application, testserver):
    report_url = 'http://localhost:6551/services/json'
    unique_id = 'http://xml.zeit.de/artikel/01'
    thread = zeit.web.core.comments.get_thread(unique_id)
    assert thread['comment_report_url'] == report_url
