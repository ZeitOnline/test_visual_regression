# -*- coding: utf-8 -*-
from zeit.cms.interfaces import ID_NAMESPACE as NS
import lxml.etree
import pyramid.httpexceptions
import mock
import pytest
import zeit.web.core.view_comment
from mock import patch
import zope
import requests
import operator


def test_comment_count_should_handle_missing_uid_param(comment_counter):
    resp = comment_counter()
    assert resp.status == '412 Precondition Failed'


def test_comment_count_should_handle_invalid_uid_param(comment_counter):
    resp = comment_counter(no_interpolation='true', unique_id='foo')
    assert resp.status == '412 Precondition Failed'


def test_comment_count_should_return_expected_json_structure_for_cp_id(
        comment_counter, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="125" url="/centerpage/article_image_asset"/>
        <node comment_count="103" url="/zeit-online/cp-content/article-01"/>
        <node comment_count="291" url="/zeit-online/cp-content/article-02"/>
    </nodes>""")

    resp = comment_counter(no_interpolation='true',
                           unique_id=NS + 'zeit-online/main-teaser-setup')

    assert 'comment_count' in resp
    cc = resp['comment_count']
    assert cc[NS + 'zeit-online/cp-content/article-01'] == '103 Kommentare'
    assert cc[NS + 'centerpage/article_image_asset'] == '125 Kommentare'
    assert cc[NS + 'zeit-online/cp-content/article-02'] == '291 Kommentare'


def test_comment_count_should_return_expected_json_structure_for_article_id(
        comment_counter, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/artikel/01"/>
    </nodes>""")

    resp = comment_counter(no_interpolation='true',
                           unique_id=NS + 'artikel/01')
    assert 'comment_count' in resp
    cc = resp['comment_count']
    assert cc[NS + 'artikel/01'] == '129 Kommentare'


def test_comment_count_should_fallback_to_zero_if_count_unavailable(
        comment_counter, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/artikel/01"/>
    </nodes>""")

    resp = comment_counter(no_interpolation='true',
                           unique_id=NS + 'zeit-magazin/test-cp/test-cp-zmo-3')
    assert 'comment_count' in resp
    cc = resp['comment_count']
    assert cc[NS + 'zeit-magazin/test-cp/essen-geniessen-spargel-lamm'] == (
        'Keine Kommentare')


def test_request_thread_should_respond(application):
    unique_id = ('/politik/deutschland/2013-07/wahlbeobachter-portraets/'
                 'wahlbeobachter-portraets')
    thread = zeit.web.core.comments.request_thread(unique_id)
    assert lxml.etree.fromstring(thread).xpath('comment_count')[0].text == '41'


def test_request_thread_should_respond_for_nonexistent(application):
    assert zeit.web.core.comments.request_thread('nosuchthread') is None


def test_comment_to_dict_should_parse_correctly(application, testserver):
    unique_id = ('/politik/deutschland/2013-07/wahlbeobachter-portraets/'
                 'wahlbeobachter-portraets')

    thread = zeit.web.core.comments.request_thread(unique_id)
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


def test_entire_thread_should_be_parsed(application, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination='foo', sort='desc')
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Skarsgard'
    assert thread_as_json['comment_count'] == 41


def test_paging_should_not_affect_comment_threads(application, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination='foo', sort='desc')
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Skarsgard'
    assert thread_as_json['comment_count'] == 41


def test_thread_should_have_valid_page_information(application, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread = zeit.web.core.comments.get_thread(unique_id)
    assert thread['page'] is None
    assert thread['page_total'] == 5

    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread = zeit.web.core.comments.get_thread(unique_id, page=2)
    assert thread['page'] == 2
    assert len(thread['comments']) == 10

    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread = zeit.web.core.comments.get_thread(unique_id, page=6)
    assert thread['comments'] == []
    assert thread['page'] == '6 (invalid)'


def test_dict_with_article_paths_and_comment_counts_should_be_created(
        monkeypatch, comment_counter):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_counts', lambda *_: """
    <?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="125" url="/centerpage/article_image_asset"/>
    </nodes>""")

    unique_id = 'http://xml.zeit.de/centerpage/article_image_asset'
    resp = comment_counter(no_interpolation='true', unique_id=unique_id)
    assert isinstance(resp, dict)
    assert resp['comment_count'][unique_id] == '125 Kommentare'


def test_rewrite_comments_url_should_rewrite_to_static_host(application):
    import zeit.web.core.comments
    url = zeit.web.core.comments.rewrite_picture_url(
        'http://localhost:6551/baaa')
    assert url == 'http://static_community/foo/baaa'


def test_post_comment_should_throw_exception_if_no_user_is_present():
    request = mock.Mock()
    request.authenticated_userid = False
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
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
    readable_comments = [
        (comment['cid'], comment['shown_num']) for comment in sorted_comments]
    assert readable_comments == (
        [(1, '1'), (6, '1.1'), (2, '2'), (4, '2.1'), (5, '2.2'), (3, '3')])


def _create_poster(monkeypatch):
    request = mock.Mock()
    request.authenticated_userid = True

    request.params = {'path': 'my/path'}
    request.session = {'user': {'uid': '123'}}
    request.cookies = {}
    context = mock.Mock()

    def util(arg):
        return {
            'community_host': 'http://foo',
            'app_servers': ['http://foo', 'http://baa']}

    monkeypatch.setattr(zope.component, 'getUtility', util)

    def post(action_url, data=None, cookies=None):
        return None
    monkeypatch.setattr(requests, 'post', post)

    def nid(me, uid):
        return 1
    monkeypatch.setattr(
        zeit.web.core.view_comment.PostComment, '_nid_by_comment_thread', nid)

    return zeit.web.core.view_comment.PostComment(context, request)


def test_post_comment_should_initialise_if_user_is_present(monkeypatch):
    poster = _create_poster(monkeypatch)

    assert poster.path == 'my/path'
    assert isinstance(poster.context, mock.Mock)
    assert poster.community_host == 'http://foo'
    assert poster.status == []


@pytest.mark.parametrize("path, comment, pid, action", [
    ('path', 'my comment', '1', 'comment')])
def test_post_comment_should_raise_exception_if_no_post_is_used(
        monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "GET"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['cid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('/my/path', None, None, 'comment'),
    (None, None, None, 'comment'),
    (None, 'my_comment', None, 'comment')])
def test_post_comment_should_raise_exception_if_params_are_wrong(
        monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['cid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('my/path', None, None, 'report'),
    ('my/path', 'my_comment', None, 'report'),
    ('my/path', None, 1, 'report')])
def test_post_report_should_raise_exception_if_params_are_wrong(
        monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['cid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('my/path', None, None, 'recommend')])
def test_post_recommondation_should_raise_exception_if_params_are_wrong(
        monkeypatch, path, pid, comment, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"

    poster.path = path
    poster.request.params['comment'] = comment
    poster.request.params['cid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPInternalServerError):
        poster.post_comment()


endpoint_agatho = (
    ('http://foo/agatho/thread/my/path',),
    {'cookies': {},
     'data': {
     'comment': 'my comment',
     'pid': None,
     'uid': '123',
     'nid': 1,
     'subject': '[empty]'}})

endpoint_report = (
    ('http://foo/services/json?callback=zeit',),
    {'cookies': {},
     'data': {
     'note': 'my comment',
     'content_id': '1',
     'method': 'flag.flagnote',
     'flag_name': 'kommentar_bedenklich',
     'uid': '123', }})

endpoint_recommend = (
    ('http://foo/services/json?callback=zeit',),
    {'cookies': {},
     'data': {
     'content_id': '1',
     'method': 'flag.flag',
     'flag_name': 'leser_empfehlung',
     'uid': '123', }})


@pytest.mark.parametrize("path, comment, pid, action, result", [
    ('my/path', 'my comment', None, 'comment', endpoint_agatho)])
def test_post_comments_should_post_with_correct_arguments(
        monkeypatch, path, comment, pid, result, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = comment
    poster.path = path
    poster.request.params['action'] = action
    poster.request.params['cid'] = pid
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
def test_post_comments_should_get_with_correct_arguments(
        monkeypatch, path, comment, pid, result, action):
    poster = _create_poster(monkeypatch)
    poster.request.method = "POST"
    poster.request.params['comment'] = comment
    poster.path = path
    poster.request.params['action'] = action
    poster.request.params['cid'] = pid
    with patch.object(requests, 'get') as mock_method:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.content = ''
        mock_method.return_value = response
        poster.post_comment()

    expected = sorted(result[1]['data'].items(), key=operator.itemgetter(1))
    actual = sorted(
        mock_method.call_args_list[0][1]['data'].items(),
        key=operator.itemgetter(1))
    assert actual == expected
    assert result[0] == mock_method.call_args_list[0][0]


@pytest.mark.parametrize("action, path, service", [
    ('comment', 'my/article', 'http://foo/agatho/thread/my/article'),
    ('report', 'my/article', 'http://foo/services/json?callback=zeit')])
def test_action_url_should_be_created_correctly(
        monkeypatch, action, path, service):
    poster = _create_poster(monkeypatch)
    assert poster._action_url(action, path) == service


def test_invalidation_view_should_work_correctly(
        testserver, monkeypatch):
    def invalidate(arg):
        return {'community_host': 'http://foo'}

    monkeypatch.setattr(
        zeit.web.core.view_comment, 'invalidate_comment_thread', invalidate)
    unique_id = 'http://xml.zeit.de/zeit-online/article/01'

    response = requests.get(
        '%s/json/invalidate?unique_id=%s' % (testserver.url, unique_id))

    assert response.json()['msg'] == (
        u'http://xml.zeit.de/zeit-online/article/01 was invalidated')

    unique_id = '/xml.zeit.de/zeit-online/article/01'
    response = requests.get(
        '%s/json/invalidate?unique_id=%s' % (testserver.url, unique_id))

    assert response.status_code == 500

    unique_id = 'http://hrgs.de/article/01'
    response = requests.get(
        '%s/json/invalidate?unique_id=%s' % (testserver.url, unique_id))
    assert response.status_code == 500

    response = requests.get('%s/json/invalidate' % testserver.url)
    assert response.status_code == 500


def test_invalidate_view_should_respond_with_404_when_called_by_a_proxy():
    request = pyramid.testing.DummyRequest()
    setattr(request, 'host_port', 80)
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        zeit.web.core.view_comment.invalidate(request)


def test_lru_cache_should_be_invalidated_by_unique_id(testserver):
    cache_maker = zeit.web.core.comments.cache_maker
    cache_maker._cache['comment_thread'].data = {}
    requests.get('%s/zeit-online/article/01' % testserver.url)
    assert cache_maker._cache['comment_thread'].data.keys()[0] == (
        ('http://xml.zeit.de/zeit-online/article/01',))

    zeit.web.core.view_comment.invalidate_comment_thread(
        'http://xml.zeit.de/zeit-online/article/01')
    assert cache_maker._cache['comment_thread'].data == {}


def test_all_app_servers_should_be_invalidated(monkeypatch):

    def invalidate(args):
        return

    monkeypatch.setattr(
        zeit.web.core.view_comment, 'invalidate_comment_thread', invalidate)

    with patch.object(requests, 'get') as mock_method:
        response = mock.Mock()
        response.status_code = 200
        response.headers = {}
        response.content = ''
        mock_method.return_value = response
        poster = _create_poster(monkeypatch)
        poster._invalidate_app_servers('http://unique_id')

    assert mock_method.call_count == 2
    assert mock_method.call_args_list == [
        (('http://foo/json/invalidate?unique_id=http://unique_id',), {}),
        (('http://baa/json/invalidate?unique_id=http://unique_id',), {})]
