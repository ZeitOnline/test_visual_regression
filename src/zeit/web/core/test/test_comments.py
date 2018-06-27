# -*- coding: utf-8 -*-
import datetime
import itertools
import operator
import time
import urllib2

from mock import patch
import dogpile.cache.region
import lxml.etree
import mock
import pyramid.httpexceptions
import pytest
import pytz
import requests
import requests.exceptions
import requests_mock
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ID_NAMESPACE as NS
import zeit.cms.interfaces

import zeit.web.core.view
import zeit.web.core.view_comment


def test_comment_count_should_handle_missing_uid_param(testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        testbrowser('/json/comment-count')
    assert info.value.getcode() == 412


def test_comment_count_should_handle_invalid_uid_param(testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        testbrowser('/json/comment-count?unique_id=foo')
    assert info.value.getcode() == 412


def test_comment_count_should_return_expected_json_structure_for_cp_id(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="125"
         url="/zeit-magazin/centerpage/article_image_asset"/>
        <node comment_count="103" url="/zeit-online/cp-content/article-01"/>
        <node comment_count="291" url="/zeit-online/cp-content/article-02"/>
    </nodes>""")

    browser = testbrowser('/json/comment-count?unique_id=' +
                          NS + 'zeit-online/main-teaser-setup')

    assert 'comment_count' in browser.json
    cc = browser.json['comment_count']
    assert cc[NS + 'zeit-online/cp-content/article-01'] == '103 Kommentare'
    assert(cc[NS + 'zeit-magazin/'
           'centerpage/article_image_asset'] == '125 Kommentare')
    assert cc[NS + 'zeit-online/cp-content/article-02'] == '291 Kommentare'


def test_comment_count_should_return_expected_json_structure_for_article_id(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/zeit-magazin/article/01"/>
    </nodes>""")

    browser = testbrowser('/json/comment-count'
                          '?unique_id=' + NS + 'zeit-magazin/article/01')

    assert 'comment_count' in browser.json
    cc = browser.json['comment_count']
    assert cc[NS + 'zeit-magazin/article/01'] == '129 Kommentare'


def test_comment_count_should_fallback_to_zero_if_count_unavailable(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/zeit-magazin/article/01"/>
    </nodes>""")

    browser = testbrowser('/json/comment-count?unique_id=' +
                          NS + 'zeit-magazin/misc')

    assert 'comment_count' in browser.json
    cc = browser.json['comment_count']
    assert cc[NS + 'zeit-magazin/article/essen-geniessen-spargel-lamm'] == (
        'Keine Kommentare')


def test_comment_count_should_be_empty_for_link_object(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/zeit-magazin/article/01"/>
    </nodes>""")

    browser = testbrowser('/json/comment-count?unique_id=' +
                          NS + 'zeit-online/cp-content/link_teaser')

    assert 'comment_count' in browser.json
    assert not browser.json['comment_count']


def test_comment_count_should_not_request_counts_for_disabled_content(
        application, dummy_request, workingcopy):
    article = 'http://xml.zeit.de/zeit-online/article/simple'
    with checked_out(zeit.cms.interfaces.ICMSContent(article)) as co:
        co.commentsAllowed = False

    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': article, 'type': 'article'}]

    cp = zeit.content.cp.centerpage.CenterPage()
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'duo'
    area.automatic_type = 'query'
    area.count = 1
    area.automatic = True
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository['testcp'] = cp

    dummy_request.GET['unique_id'] = 'http://xml.zeit.de/testcp'
    result = zeit.web.core.view_json.json_comment_count(dummy_request)
    with mock.patch(
            'zeit.web.core.comments.Community.get_comment_counts') as count:
        assert 'Keine Kommentare' == result['comment_count'][
            'http://xml.zeit.de/zeit-online/article/simple']
        assert not count.called


def test_request_thread_should_respond(application, mockserver):
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    thread = community._request_thread('/zeit-online/article/03')
    assert lxml.etree.fromstring(thread).xpath('comment_count')[0].text == '41'


def test_request_thread_should_respond_for_nonexistent(
        application, mockserver):
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    with pytest.raises(zeit.web.core.comments.ThreadNotFound):
        community._request_thread('nosuchthread')


def test_request_thread_should_handle_non_ascii_urls(application, mockserver):
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    with pytest.raises(zeit.web.core.comments.ThreadNotFound):
        community._request_thread(u'ümläut')


def test_request_thread_should_fail_on_certain_status_codes(
        application, monkeypatch):
    def get(action_url, timeout=1):
        response = mock.Mock
        response.status_code = 300
        return response
    monkeypatch.setattr(requests, 'get', get)

    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    with pytest.raises(zeit.web.core.comments.CommunityError):
        community._request_thread('http://community/foo')


def test_request_thread_should_fail_on_timeouts(application, monkeypatch):

    def get(action_url, timeout=1):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr(requests, 'get', get)

    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    with pytest.raises(zeit.web.core.comments.CommunityError):
        community._request_thread('some_unique_id')


def test_request_thread_mode_should_produce_expected_uris(
        monkeypatch, application):

    response = requests.Response()
    response.status_code = 200
    request_get = mock.Mock(return_value=response)
    monkeypatch.setattr(requests, 'get', request_get)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    full_thread = '{}/agatho/thread/foo'.format(conf.get('agatho_host', ''))
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    community._request_thread('/foo')

    request_get.assert_called_with(full_thread, timeout=10.0)

    paginated_thread = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''), '?mode=top&page=0&rows=4&order=asc')

    community._request_thread('/foo', thread_type='paginated')

    request_get.assert_called_with(paginated_thread, timeout=10.0)

    paginated_thread = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''), '?mode=top&page=1&rows=10&order=asc')

    community._request_thread(
        '/foo', thread_type='paginated', page=1, page_size=10)

    request_get.assert_called_with(paginated_thread, timeout=10.0)

    deeplink_thread = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''), '?mode=deeplink&cid=1&rows=10&order=asc')

    community._request_thread(
        '/foo', thread_type='deeplink', cid=1, page_size=10)

    request_get.assert_called_with(deeplink_thread, timeout=10.0)

    sub_thread = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''), '?mode=sub&cid=10')

    community._request_thread(
        '/foo', thread_type='sub_thread', cid=10)

    request_get.assert_called_with(sub_thread, timeout=10.0)

    recommendation = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''),
        '?mode=recommendations&recommendationtype=leser_empfehlung'
        '&page=1&rows=4&order=asc')

    community._request_thread(
        '/foo', thread_type='recommendation', page=1, page_size=4)

    request_get.assert_called_with(recommendation, timeout=10.0)

    promotion = '{}/agatho/thread/foo{}'.format(
        conf.get('agatho_host', ''),
        '?mode=recommendations&recommendationtype=kommentar_empfohlen'
        '&page=1&rows=4&order=asc')

    community._request_thread(
        '/foo', thread_type='promotion', page=1, page_size=4)

    request_get.assert_called_with(promotion, timeout=10.0)


def test_comment_to_dict_should_parse_correctly(application):
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    thread = community._request_thread('/zeit-online/article/03')
    comment_xml = lxml.etree.fromstring(thread).xpath('//comment')[0]
    comment = zeit.web.core.comments.comment_to_dict(comment_xml)
    assert comment['name'] == 'Skarsgard'
    assert comment['text'] == ("<p>Komik</p><p>Ein Iraner,der findet,"
                               "dass die Deutschen zu wenig meckern..."
                               "^^</p>\n")

    # Dont' show subject if taken from comment itself
    comment_xml.xpath('//comment')[0][0].text = 'Ein Iraner'
    comment = zeit.web.core.comments.comment_to_dict(comment_xml)
    assert comment['text'] == ("<p>Ein Iraner,der findet,"
                               "dass die Deutschen zu wenig meckern..."
                               "^^</p>\n")

    # Remove subject
    del comment_xml.xpath('//comment')[0][0]
    comment = zeit.web.core.comments.comment_to_dict(comment_xml)
    assert comment['text'] == ("<p>Ein Iraner,der findet,"
                               "dass die Deutschen zu wenig meckern..."
                               "^^</p>\n")

    # Handle empty commenter names gracefully
    comment_xml = lxml.etree.fromstring(thread).xpath('//comment')[1]
    comment = zeit.web.core.comments.comment_to_dict(comment_xml)
    assert comment['name'] == ''


def test_entire_thread_should_be_parsed(application):
    unique_id = 'http://xml.zeit.de/zeit-online/article/03'
    thread = zeit.web.core.comments.get_thread(unique_id, sort='desc')
    first = thread['comments'].pop(0)
    last = thread['comments'].pop()
    assert first['cid'] == 2969196
    assert last['cid'] == 2968470
    assert thread['comment_count'] == 41
    assert len(first['replies']) == 0
    assert len(last['replies']) == 1


def test_thread_should_have_valid_page_information(application):
    unique_id = 'http://xml.zeit.de/zeit-online/article/03'
    thread = zeit.web.core.comments.get_thread(unique_id)
    assert thread['pages']['current'] is None
    assert thread['pages']['total'] == 4

    thread = zeit.web.core.comments.get_thread(unique_id, page=2)
    assert thread['pages']['current'] == 2
    assert len(thread['comments']) == 4

    # check for page not present
    thread = zeit.web.core.comments.get_thread(unique_id, page=6)
    assert thread['pages']['current'] == 1
    assert len(thread['comments']) == 4

    thread = zeit.web.core.comments.get_thread(unique_id, cid=2968742)
    assert thread['pages']['current'] == 3

    # ignore page param if comment id is supplied
    thread = zeit.web.core.comments.get_thread(unique_id, page=2, cid=2968742)
    assert thread['pages']['current'] == 3

    # comment id AND sort descendant
    thread = zeit.web.core.comments.get_thread(unique_id, sort='desc',
                                               cid=2968742)
    assert thread['pages']['current'] == 2


def test_dict_with_article_paths_and_comment_counts_should_be_created(
        monkeypatch, testbrowser):
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="125"
         url="/zeit-magazin/centerpage/article_image_asset"/>
    </nodes>""")

    browser = testbrowser('/json/comment-count?unique_id=' +
                          NS + 'zeit-magazin/centerpage/article_image_asset')

    assert 'comment_count' in browser.json
    cc = browser.json['comment_count']
    assert(cc[NS + 'zeit-magazin/'
           'centerpage/article_image_asset'] == '125 Kommentare')


def test_rewrite_comments_url_should_rewrite_to_static_host(application):
    import zeit.web.core.comments
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    url = zeit.web.core.comments.rewrite_picture_url(
        conf['community_host'] + '/foo.jpg')
    assert url == 'http://static_community/foo.jpg'


def test_post_comment_should_throw_exception_if_no_user_is_present():
    request = mock.Mock()
    request.user = {}
    with pytest.raises(pyramid.httpexceptions.HTTPForbidden):
        zeit.web.core.view_comment.PostComment(mock.Mock(), request)


def test_comment_tree_should_be_flattened_on_level_two():
    cid_1 = dict(
        in_reply=None,
        cid=1)

    cid_2 = dict(
        in_reply=None,
        cid=2)

    cid_3 = dict(
        in_reply=None,
        cid=3)

    cid_4 = dict(
        in_reply=2,
        cid=4)

    cid_5 = dict(
        in_reply=2,
        cid=5)

    cid_6 = dict(
        in_reply=1,
        cid=6)

    comments = [cid_1, cid_2, cid_3, cid_4, cid_5, cid_6]

    sorted_comments = zeit.web.core.comments._sort_comments(comments)[0]

    # flatten list here to test, if the structure will be valid
    # The flattening now actually happens in z.w.c.comments.get_thread
    sorted_comments = list(itertools.chain(
        *[[li[0]] + li[1] for li in sorted_comments.values()]))

    readable_comments = [
        (comment['cid'], comment['shown_num']) for comment in sorted_comments]
    assert readable_comments == (
        [(1, '1'), (6, '1.1'), (2, '2'), (4, '2.1'), (5, '2.2'), (3, '3')])


def test_comments_should_have_correct_order_when_paginated():
    cid_1 = dict(
        in_reply=None,
        cid=1)

    cid_2 = dict(
        in_reply=None,
        cid=2)

    cid_3 = dict(
        in_reply=2,
        cid=3)

    comments = [cid_1, cid_2, cid_3]

    sorted_comments = zeit.web.core.comments._sort_comments(
        comments, offset=2)[0]

    sorted_comments = list(itertools.chain(
        *[[li[0]] + li[1] for li in sorted_comments.values()]))

    readable_comments = [
        (comment['cid'], comment['shown_num']) for comment in sorted_comments]
    assert readable_comments == (
        [(1, '3'), (2, '4'), (3, '4.1')])


def test_sort_order_should_be_derived_correctly():
    view = zeit.web.core.view.CommentMixin()
    view.request = mock.Mock()
    view.context = mock.Mock()

    # Sort order should be desc, if recent_comments_first is true
    # and no user parameter is set.
    view.request.params = {}
    view.context.recent_comments_first = True
    assert view._get_comment_sorting() == 'desc'

    # Sort order should be asc, if recent_comments_first is true,
    # but user parameter indicates asc.
    view.request.params = {'sort': 'asc'}
    view.context.recent_comments_first = True
    assert view._get_comment_sorting() == 'asc'

    # Defaul sort order should be asc, if recent_comments_first is False
    view.request.params = {}
    view.context.recent_comments_first = False
    assert view._get_comment_sorting() == 'asc'


def _create_poster(monkeypatch):
    request = mock.Mock()
    request.user = {'ssoid': '123', 'uid': '123', 'name': 'foo'}
    request.session = {}

    request.params = {'path': 'my/path'}
    request.GET = request.POST = request.params
    request.cookies = {}
    context = mock.Mock()

    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    settings['community_host'] = 'http://foo'
    settings['app_servers'] = ['http://foo', 'http://baa']

    def post(action_url, data=None, cookies=None):
        return None
    monkeypatch.setattr(requests, 'post', post)

    def fans(me, uid, pid):
        return None, []
    monkeypatch.setattr(
        zeit.web.core.view_comment.PostComment, '_get_recommendations', fans)

    monkeypatch.setattr(
        zeit.web.core.view_comment.PostComment, '_ensure_comment_thread',
        lambda me, uid: None)

    def dont_cache(self, key, creator, *args, **kw):
        return creator()
    monkeypatch.setattr(
        dogpile.cache.region.CacheRegion, 'get_or_create', dont_cache)

    return zeit.web.core.view_comment.PostComment(context, request)


def test_post_comment_should_initialise_if_user_is_present(
        application, monkeypatch):
    poster = _create_poster(monkeypatch)

    assert poster.path == 'my/path'
    assert isinstance(poster.context, mock.Mock)
    assert poster.community_host == 'http://foo'
    assert poster.status == []


@pytest.mark.parametrize("path, comment, pid, action", [
    ('path', 'my comment', '1', 'comment')])
def test_post_comment_should_raise_exception_if_no_post_is_used(
        application, monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "GET"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPMethodNotAllowed):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('/my/path', None, None, 'comment'),
    (None, None, None, 'comment'),
    (None, 'my_comment', None, 'comment')])
def test_post_comment_should_raise_exception_if_params_are_wrong(
        application, monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPBadRequest):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('my/path', None, None, 'report'),
    ('my/path', 'my_comment', None, 'report'),
    ('my/path', None, 1, 'report')])
def test_post_report_should_raise_exception_if_params_are_wrong(
        application, monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPBadRequest):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('my/path', None, None, 'recommend')])
def test_post_recommondation_should_raise_exception_if_params_are_wrong(
        application, monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPBadRequest):
        poster.post_comment()


endpoint_agatho = (
    ('http://foo/agatho/thread/my/path',),
    {'cookies': {},
     'data': {
     'comment': 'my comment',
     'pid': None,
     'uid': '123',
     'article_premoderate': 'true',
     'subject': '[empty]'}})

endpoint_report = (
    ('http://foo/services/json?callback=zeit',),
    {'cookies': {},
     'data': {
     'note': 'my comment',
     'content_id': 1,
     'method': 'flag.flagnote',
     'flag_name': 'kommentar_bedenklich',
     'uid': '123', }})

endpoint_recommend = (
    ('http://foo/services/json?callback=zeit',),
    {'cookies': {},
     'data': {
     'content_id': 1,
     'action': 'flag',
     'method': 'flag.flag',
     'flag_name': 'leser_empfehlung',
     'uid': '123', }})


@pytest.mark.parametrize("path, comment, pid, action, result", [
    ('my/path', 'my comment', None, 'comment', endpoint_agatho)])
def test_post_comment_should_post_with_correct_arguments(
        application, monkeypatch, path, comment, pid, result, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = comment
    poster.path = path
    poster.request.params['action'] = action
    poster.request.params['pid'] = pid
    with patch.object(requests, 'post') as mock_method:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.content = ''
        mock_method.return_value = response
        poster.post_comment()

    expected = sorted(result[1]['data'].items(), key=operator.itemgetter(1))
    actual = sorted(
        mock_method.call_args[1]['data'].items(), key=operator.itemgetter(1))
    assert actual == expected
    assert result[0] == mock_method.call_args[0]


@pytest.mark.parametrize("path, comment, pid, action, result", [
    ('my/path', None, '1', 'recommend', endpoint_recommend),
    ('my/path', 'my comment', '1', 'report', endpoint_report)])
def test_post_comment_should_get_with_correct_arguments(
        application, monkeypatch, path, comment, pid, result, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = comment
    poster.path = path
    poster.request.params['action'] = action
    poster.request.params['pid'] = pid
    with patch.object(requests, 'get') as mock_method:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.content = ''
        mock_method.return_value = response
        poster.post_comment()
    expected = sorted(result[1]['data'].items(), key=operator.itemgetter(1))
    assert result[0] in dict(mock_method.call_args_list)
    actual = sorted(
        dict(mock_method.call_args_list).get(result[0])['data'].items(),
        key=operator.itemgetter(1))
    assert actual == expected


@pytest.mark.parametrize("path, comment, pid, action, result", [
    ('my/path', 'my comment', None, 'comment', endpoint_agatho)])
def test_invalidation_should_be_called_on_successful_post(
        application, monkeypatch, path, comment, pid, result, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = comment
    poster.path = path
    poster.request.params['action'] = action
    poster.request.params['pid'] = pid
    with patch.object(requests, 'post') as mock_method:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.content = ''
        mock_method.return_value = response
        with patch.object(
                zeit.web.core.view_comment, 'invalidate_comment_thread') as iv:
            poster.post_comment()

    assert iv.call_args[0][0] == 'http://xml.zeit.de/my/path'


@pytest.mark.parametrize("action, path, service", [
    ('comment', 'my/article', 'http://foo/agatho/thread/my/article'),
    ('report', 'my/article', 'http://foo/services/json?callback=zeit')])
def test_action_url_should_be_created_correctly(
        application, monkeypatch, action, path, service):
    poster = _create_poster(monkeypatch)
    assert poster._action_url(action, path) == service


@pytest.mark.parametrize("action", ['comment', 'report'])
def test_post_comment_should_set_lock(application, action):
    request = pyramid.testing.DummyRequest()
    request.user = {'ssoid': '123', 'name': 'foo'}
    pc = zeit.web.core.view_comment.PostComment(mock.Mock(), request)
    pc.lock_duration = datetime.timedelta(0, 0.5)
    locker = pc.handle_comment_locking

    locker(request, action)

    assert request.session['lock_commenting'] is True

    with pytest.raises(pyramid.httpexceptions.HTTPForbidden):
        locker(request, action)

    time.sleep(0.5)

    locker(request, action)
    assert request.session['lock_commenting'] is True


@pytest.mark.parametrize("action", ['recommend', 'promote', 'demote'])
def test_post_comment_should_not_set_lock(application, action):
    request = pyramid.testing.DummyRequest()
    request.user = {'ssoid': '123', 'name': 'foo'}
    pc = zeit.web.core.view_comment.PostComment(mock.Mock(), request)
    pc.lock_duration = datetime.timedelta(0, 0.5)
    locker = pc.handle_comment_locking
    locker(request, action)

    assert request.session.get('lock_commenting') is None


def test_post_comment_should_not_expose_requests_timeout_exception(
        application, monkeypatch, dummy_request):

    dummy_request.method = 'POST'
    dummy_request.POST.update({
        'path': 'zeit-magazin/article/01', 'action': 'comment', 'comment': ' '
    })
    dummy_request.user = {'ssoid': '123', 'uid': '123', 'name': 'foo'}

    def post(url, **kw):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, 'post', post)

    view = zeit.web.core.view_comment.PostComment(mock.Mock(), dummy_request)
    monkeypatch.setattr(view, '_ensure_comment_thread', lambda *args: None)

    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        view.post_comment()


def test_get_thread_should_return_none_on_errors(application, monkeypatch):

    def request_thread(unique_id, sort="asc", page=None, cid=None):
        return {'request_failed': datetime.datetime.utcnow()}
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_thread', request_thread)

    assert zeit.web.core.comments.get_thread('http://unique_id') is None


def test_get_thread_should_invalidate_on_unloaded_threads(application,
                                                          monkeypatch):

    def request_thread(unique_id, sort="asc", page=None, cid=None):
        raise zeit.web.core.comments.CommunityError()
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_thread', request_thread)

    try:
        with patch.object(
                zeit.web.core.view_comment,
                'invalidate_comment_thread') as mock_method:
            zeit.web.core.comments.get_thread(
                'http://unique_id', invalidate_delta=0)
    except:
        pass
    assert mock_method.call_args_list == [(('http://unique_id',), {})]


def test_get_thread_should_not_invalidate_on_unloaded_threads(application,
                                                              monkeypatch):

    def request_thread(unique_id, sort="asc", page=None, cid=None):
        return {'request_failed': datetime.datetime.utcnow()}
    monkeypatch.setattr(
        zeit.web.core.comments.Community, '_request_thread', request_thread)

    try:
        with patch.object(
                zeit.web.core.view_comment,
                'invalidate_comment_thread') as mock_method:
            zeit.web.core.comments.get_thread(
                'http://unique_id', invalidate_delta=5)
    except:
        pass

    assert mock_method.call_args_list == []


def test_article_view_should_have_short_caching_time_on_unloadable_thread(
        application, testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments.SHORT_TERM_CACHE, 'expiration_time', 1)
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    assert browser.headers.get('cache-control') == 'max-age=10'

    monkeypatch.setattr(
        zeit.web.core.comments.Community, 'is_healthy', lambda self: False)
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    select = browser.cssselect
    assert browser.headers.get('cache-control') == 'max-age=1'
    assert select('.comment-section__message')[0].text_content().strip() == (
        u'Ein technischer Fehler ist aufgetreten. Die Kommentare '
        u'zu diesem Artikel konnten nicht geladen werden. Bitte '
        u'entschuldigen Sie diese Störung.')


def test_community_maintenance_should_be_created_from_xml():
    xml = lxml.etree.fromstring(
        """
        <community_maintenance>
            <active>true</active>
            <scheduled>true</scheduled>
            <begin>2010-10-10T10:10:10.10+01:00</begin>
            <end>2020-10-10T10:10:10.10+01:00</end>
            <text_scheduled></text_scheduled>
            <text_active></text_active>
        </community_maintenance>
        """)

    maintenance = {
        'active': False,
        'scheduled': False,
        'begin': None,
        'end': None,
        'text_scheduled': (u'Aufgrund von Wartungsarbeiten sind die '
                           u'Kommentarfunktionen in Kürze vorübergehend '
                           u'nicht mehr verfügbar. Wir bitten um Ihr '
                           u'Verständnis.'),
        'text_active': (u'Aufgrund von Wartungsarbeiten sind die '
                        u'Kommentarfunktionen vorübergehend '
                        u'nicht mehr verfügbar. Wir bitten um Ihr '
                        u'Verständnis.')
    }

    res = zeit.web.core.comments._maintenance_from_xml(xml, maintenance)
    begin = datetime.datetime(
        2010, 10, 10, 9, 10, 10, 100000, tzinfo=pytz.utc)
    end = datetime.datetime(2020, 10, 10, 9, 10, 10, 100000, tzinfo=pytz.utc)
    assert res['active']
    assert res['scheduled']
    assert isinstance(res['begin'], datetime.datetime)
    assert res['begin'] == begin
    assert isinstance(res['end'], datetime.datetime)
    assert res['end'] == end
    assert res['text_scheduled'] == maintenance['text_scheduled']
    assert res['text_active'] == maintenance['text_active']

    xml = lxml.etree.fromstring(
        """
        <community_maintenance>
            <text_scheduled>text_scheduled</text_scheduled>
            <text_active>text_active</text_active>
        </community_maintenance>
        """)
    res = zeit.web.core.comments._maintenance_from_xml(xml, maintenance)
    assert res['text_scheduled'] == 'text_scheduled'
    assert res['text_active'] == 'text_active'


def test_community_maintenance_should_be_scheduled_correctly():
    maintenance = {
        'active': False,
        'scheduled': True,
        'begin': datetime.datetime(
            2000, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc),
        'end': datetime.datetime(
            2299, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc),
        'text_scheduled': (u'Aufgrund von Wartungsarbeiten sind die '
                           u'Kommentarfunktionen in Kürze vorübergehend '
                           u'nicht mehr verfügbar. Wir bitten um Ihr '
                           u'Verständnis.'),
        'text_active': (u'Aufgrund von Wartungsarbeiten sind die '
                        u'Kommentarfunktionen vorübergehend '
                        u'nicht mehr verfügbar. Wir bitten um Ihr '
                        u'Verständnis.')
    }
    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] is True

    maintenance['active'] = False
    maintenance['end'] = datetime.datetime(
        2001, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] is False

    maintenance['active'] = False
    maintenance['begin'] = datetime.datetime(
        2299, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2299, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] is False

    maintenance['active'] = True
    maintenance['begin'] = datetime.datetime(
        2299, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2299, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] is True

    maintenance['active'] = True
    maintenance['begin'] = datetime.datetime(
        2000, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2001, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] is True


def test_community_maintenance_should_be_created_from_config(application):
    maintenance = zeit.web.core.comments.community_maintenance()
    assert maintenance['active'] is False
    assert maintenance['text_active'] == 'text_active'


def test_community_maintenance_should_be_disabled_for_invalid_url(application):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['community_maintenance'] = 'http://xml.zeit.de/nonexistent'
    maintenance = zeit.web.core.comments.community_maintenance()
    assert not maintenance['active']
    assert maintenance['text_active'].startswith(u'Aufgrund')


@pytest.mark.parametrize("header, state, status_code, premoderation_article", [
    ({'x-premoderation': 'true'}, True, 202, True),
    ({'x-premoderation': 'false'}, False, 200, True),
    ({'x-premoderation': 'false'}, False, 200, False),
    ({'x-premoderation': 'true'}, False, 200, True),
    ({}, False, 200, True),
    ({}, False, 200, False)])
def test_post_comment_should_have_correct_premoderation_states(
        application, monkeypatch, header, state, status_code,
        premoderation_article):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = 'my comment'
    poster.path = 'my/path'
    poster.request.params['action'] = 'comment'
    poster.request.params['pid'] = None
    with patch.object(requests, 'post') as mock_method:
        response = mock.Mock()
        response.status_code = status_code
        response.headers = header
        response.content = ''
        mock_method.return_value = response
        ret_value = poster.post_comment()
        assert ret_value['response']['premoderation_user'] is state
        if ((state and status_code == 202) or
                premoderation_article is True):
            assert ret_value['response']['premoderation'] is True


def test_user_comment_should_have_expected_structure(application):
    xml_str = """
<item>
    <cid>1</cid>
    <title>[empty]</title>
    <description>&lt;p&gt;Ich praezisiere.&lt;/p&gt;</description>
    <pubDate>2015-11-17T10:39:50+00:00</pubDate>
    <cms_uniqueId>http://www.zeit.de/zeit-magazin/article/01</cms_uniqueId>
</item>"""

    xml = lxml.etree.fromstring(xml_str)
    comment = zeit.web.core.comments.UserComment(xml)
    assert comment.cid == 1
    assert comment.__name__ == 1
    assert comment.description == '<p>Ich praezisiere.</p>'
    assert comment.publication_date.isoformat() == '2015-11-17T10:39:50+00:00'
    assert comment.uniqueId == 'http://community.zeit.de/comment/1'
    assert comment.title == '[empty]'
    assert comment.referenced_content.uniqueId == (
        'http://xml.zeit.de/zeit-magazin/article/01')

    xml_str = """
        <item>
            <cid>1</cid>
            <title></title>
            <description></description>
            <pubDate></pubDate>
            <cms_uniqueId></cms_uniqueId>
        </item>"""

    xml = lxml.etree.fromstring(xml_str)
    comment = zeit.web.core.comments.UserComment(xml)
    assert comment.cid == 1
    assert comment.description is None
    assert comment.publication_date is None
    assert comment.uniqueId == 'http://community.zeit.de/comment/1'


def test_user_comments_should_raise_exception_if_no_cid_given(application):
    xml_str = '<item><cid></cid></item>'
    xml = lxml.etree.fromstring(xml_str)
    with pytest.raises(zeit.web.core.comments.NoValidComment):
        zeit.web.core.comments.UserComment(xml)

    xml_str = '<item></item>'
    xml = lxml.etree.fromstring(xml_str)
    with pytest.raises(zeit.web.core.comments.NoValidComment):
        zeit.web.core.comments.UserComment(xml)

    xml_str = '<item><cid>a</cid></item>'
    xml = lxml.etree.fromstring(xml_str)
    with pytest.raises(zeit.web.core.comments.NoValidComment):
        zeit.web.core.comments.UserComment(xml)


def test_user_comment_thread_should_have_expected_structure(application):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    thread = community.get_user_comments(author)
    assert thread['uid'] == 172432
    assert thread['published_total'] == 14
    assert thread['page'] == 1
    assert thread['page_total'] == 3
    assert thread['sort'] == 'DESC'
    assert thread['rows'] == 6
    assert len(thread['comments']) == 6


def test_request_thread_should_be_called_only_once_by_article_and_comment_esi(
        testserver):
    # Due to ESI, these are 2 independent requests, so we allow them each one
    # (but not more!!) request to the community (the health check comes on top
    # of that, but it doesn't count since it is memcached).
    # XXX The test should be more precise and catch all community requests.
    with mock.patch(
            'zeit.web.core.comments.Community._request_thread') as req_thread:
        req_thread.return_value = None
        r = requests.get('{}/zeit-online/article/01'.format(testserver.url))
        r.raise_for_status()
        assert req_thread.call_count == 2


def test_post_comment_should_create_commentsection_with_correct_x_unique_id(
        application):
    unique_id = 'http://xml.zeit.de/zeit-online/article/01'
    zeit.web.core.application.FEATURE_TOGGLES.set('https')

    with requests_mock.Mocker() as m:
        zwcs = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        host = zwcs.get('community_host')
        m.get('{}/agatho/health_check'.format(host), status_code=200)
        m.post('{}/agatho/commentsection'.format(host), status_code=204)
        m.user = {'ssoid': '123', 'uid': '123', 'name': 'foo'}
        m.params = {
            'path': 'zeit-magazin/article/01',
            'action': 'comment', 'comment': ' '}
        view = zeit.web.core.view_comment.PostComment(mock.Mock(), m)
        view._ensure_comment_thread(unique_id)
        assert unique_id in view.status[0]


def test_thread_template_should_render_adplace(
        application, dummy_request, tplbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    browser = tplbrowser(
        'zeit.web.core:templates/inc/comments/thread.html', view=view)
    assert browser.cssselect('.comment__ad')
    assert browser.cssselect('.comment__ad script')


def test_smoke_comment_admin(testbrowser, application):
    extensions = application.zeit_app.config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions)
    with mock.patch.dict(extensions.descriptors, {
            'user': pyramid.decorator.reify(lambda x: {
                'ssoid': 123,
                'has_community_data': True,
                'uid': 123,
            })}):
        testbrowser('/admin/test-comments')


def test_smoke_post_on_article(testserver, application):
    resp = requests.post(
        '{}/zeit-online/article/01'.format(testserver.url),
        allow_redirects=False)
    assert resp.status_code == 403

    extensions = application.zeit_app.config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions)
    with mock.patch.dict(extensions.descriptors, {
            'user': pyramid.decorator.reify(lambda x: {
                'ssoid': 123,
                'has_community_data': True,
                'uid': 123,
            })}):

        resp = requests.post(
            '{}/zeit-online/article/01'.format(testserver.url),
            allow_redirects=False)
        assert resp.status_code == 303


@pytest.mark.parametrize('toggle, host, path', [
    ('set', 'community_profile_url', '/comment/edit/%cid%'),
    ('unset', 'community_admin_host',
     '/9e7bf051-2299-43e4-b5e6-1fa81d097dbd/thread/%cid%')])
def test_moderation_url_should_be_set_according_to_toggle(
        application, toggle, host, path):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    mixin = zeit.web.core.view.CommentMixin()
    mixin.context = context

    getattr(zeit.web.core.application.FEATURE_TOGGLES, toggle)(
        'zoca_moderation_launch')
    assert mixin.moderation_url == conf.get(host) + path
