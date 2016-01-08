# -*- coding: utf-8 -*-
import datetime
import itertools
import operator
import time

from mock import patch
import dogpile.cache.region
import lxml.etree
import mock
import pyramid.httpexceptions
import pytest
import pytz
import requests
import zope.component

from zeit.cms.interfaces import ID_NAMESPACE as NS
import zeit.web.core.view_comment


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


def test_request_thread_should_respond(application, mockserver):
    unique_id = ('/politik/deutschland/2013-07/wahlbeobachter-portraets/'
                 'wahlbeobachter-portraets')
    thread = zeit.web.core.comments.request_thread(unique_id)
    assert lxml.etree.fromstring(thread).xpath('comment_count')[0].text == '41'


def test_request_thread_should_respond_for_nonexistent(
        application, mockserver):
    assert zeit.web.core.comments.request_thread('nosuchthread') is None


def test_request_thread_should_handle_non_ascii_urls(application, mockserver):
    assert zeit.web.core.comments.request_thread(u'ümläut') is None


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

    # Handle empty commenter names gracefully
    comment_xml = lxml.etree.fromstring(thread).xpath('//comment')[1]
    comment = zeit.web.core.comments.comment_to_dict(comment_xml)
    assert comment['name'] == ''


def test_entire_thread_should_be_parsed(application, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread = zeit.web.core.comments.get_thread(unique_id, sort='desc')
    first = thread['comments'].pop(0)
    last = thread['comments'].pop()
    assert first['cid'] == 2969196
    assert last['cid'] == 2968470
    assert thread['comment_count'] == 41
    assert len(first['replies']) == 0
    assert len(last['replies']) == 1


def test_thread_should_have_valid_page_information(application, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
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
    request.authenticated_userid = None
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


def _create_poster(monkeypatch):
    request = mock.Mock()
    request.authenticated_userid = '123'

    request.params = {'path': 'my/path'}
    request.GET = request.POST = request.params
    request.session = {'user': {'uid': '123'}}
    request.session['user']['name'] = 'foo'
    request.cookies = {}
    context = mock.Mock()

    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    settings['community_host'] = 'http://foo'
    settings['app_servers'] = ['http://foo', 'http://baa']

    def post(action_url, data=None, cookies=None):
        return None
    monkeypatch.setattr(requests, 'post', post)

    def fans(me, uid, pid):
        return []
    monkeypatch.setattr(
        zeit.web.core.view_comment.PostComment, '_get_recommendations', fans)

    def nid(me, uid):
        return 1
    monkeypatch.setattr(
        zeit.web.core.view_comment.PostComment, '_nid_by_comment_thread', nid)

    def dont_cache(self, key, creator, *args, **kw):
        return creator()
    monkeypatch.setattr(
        dogpile.cache.region.CacheRegion, 'get_or_create', dont_cache)

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
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPMethodNotAllowed):
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
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPBadRequest):
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
    poster.request.params['pid'] = pid
    poster.request.params['action'] = action
    with pytest.raises(pyramid.httpexceptions.HTTPBadRequest):
        poster.post_comment()


@pytest.mark.parametrize("path, comment, pid, action", [
    ('my/path', None, None, 'recommend')])
def test_post_recommondation_should_raise_exception_if_params_are_wrong(
        monkeypatch, path, pid, comment, action):
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
     'nid': 1,
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
        monkeypatch, path, comment, pid, result, action):
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
        monkeypatch, action, path, service):
    poster = _create_poster(monkeypatch)
    assert poster._action_url(action, path) == service


@pytest.mark.parametrize("action", ['comment', 'report'])
def test_post_comment_should_set_lock(application, action):
    request = mock.Mock()
    request.session = {'user': {'name': 'foo'}}
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
    request = mock.Mock()
    request.session = {'user': {'name': 'foo'}}
    pc = zeit.web.core.view_comment.PostComment(mock.Mock(), request)
    pc.lock_duration = datetime.timedelta(0, 0.5)
    locker = pc.handle_comment_locking
    locker(request, action)

    assert request.session.get('lock_commenting') is None


def test_request_thread_should_fail_on_certain_status_codes(
        application, monkeypatch):
    def get(action_url, timeout=1):
        response = mock.Mock
        response.status_code = 300
        return response
    monkeypatch.setattr(requests, 'get', get)

    assert 'request_failed' in zeit.web.core.comments.request_thread(
        'http://community/foo')


def test_request_thread_should_fail_on_timeouts(application, monkeypatch):

    def get(action_url, timeout=1):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr(requests, 'get', get)

    assert 'request_failed' in zeit.web.core.comments.request_thread(
        'http://community/foo')


def test_get_thread_should_raise_exception_on_unloaded_threads(application,
                                                               monkeypatch):

    def request_thread(unique_id, sort="asc", page=None, cid=None):
        return {'request_failed': datetime.datetime.utcnow()}
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)

    with pytest.raises(zeit.web.core.comments.ThreadNotLoadable):
        zeit.web.core.comments.get_thread('http://unique_id')


def test_get_thread_should_invalidate_on_unloaded_threads(application,
                                                          monkeypatch):

    def request_thread(unique_id, sort="asc", page=None, cid=None):
        return {'request_failed': datetime.datetime.utcnow()}
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)

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
        zeit.web.core.comments, 'request_thread', request_thread)

    try:
        with patch.object(
                zeit.web.core.view_comment,
                'invalidate_comment_thread') as mock_method:
            zeit.web.core.comments.get_thread(
                'http://unique_id', invalidate_delta=5)
    except:
        pass

    assert mock_method.call_args_list == []


def test_article_view_should_set_comments_not_loadable_prop(
        application, monkeypatch):
    def get_thread(
            unique_id, sort='asc', page=None, cid=None, invalidate_delta=5):
        raise zeit.web.core.comments.ThreadNotLoadable()
    monkeypatch.setattr(zeit.web.core.comments, 'get_thread', get_thread)

    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    request = pyramid.testing.DummyRequest()
    article = zeit.web.magazin.view_article.Article(context, request)

    assert article.comments_loadable

    article.comments

    assert not article.comments_loadable

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    article = zeit.web.site.view_article.Article(context, request)

    assert article.comments_loadable

    article.comments

    assert not article.comments_loadable


def test_article_view_should_have_short_caching_time_on_unloadable_thread(
        application, testbrowser, testserver, monkeypatch):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert browser.headers.get('cache-control') == 'max-age=10'

    def get_thread(
            unique_id, sort='asc', page=None, cid=None, invalidate_delta=5):
        raise zeit.web.core.comments.ThreadNotLoadable()
    monkeypatch.setattr(zeit.web.core.comments, 'get_thread', get_thread)
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert browser.headers.get('cache-control') == 'max-age=5'
    assert browser.cssselect('.comment-section__message')[0].text.strip() == (
        u'Ein technischer Fehler ist aufgetreten. Die Kommentare '
        u'zu diesem Artikel konnten nicht geladen werden. Bitte '
        u'entschuldigen Sie diese Störung.')

    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert browser.headers.get('cache-control') == 'max-age=5'


def test_community_maintenance_should_be_created_from_xml():
    xml = lxml.etree.fromstring(
        """
        <community_maintenance>
            <active>true</active>
            <scheduled>true</scheduled>
            <begin>2010-10-10T10:10:10.10+00:00</begin>
            <end>2020-10-10T10:10:10.10+00:00</end>
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
        2010, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    end = datetime.datetime(2020, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    assert res['active']
    assert res['scheduled']
    assert res['begin'] == begin
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
        maintenance)['active'] == True

    maintenance['active'] = False
    maintenance['end'] = datetime.datetime(
        2001, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] == False

    maintenance['active'] = False
    maintenance['begin'] = datetime.datetime(
        2299, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2299, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] == False

    maintenance['active'] = True
    maintenance['begin'] = datetime.datetime(
        2299, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2299, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] == True

    maintenance['active'] = True
    maintenance['begin'] = datetime.datetime(
        2000, 10, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)
    maintenance['end'] = datetime.datetime(
        2001, 12, 10, 10, 10, 10, 100000, tzinfo=pytz.utc)

    assert zeit.web.core.comments._derive_maintenance_from_schedule(
        maintenance)['active'] == True


def test_community_maintenance_should_be_created_from_config(application):
    maintenance = zeit.web.core.comments.community_maintenance()
    assert maintenance['active'] == False
    assert maintenance['text_active'] == 'text_active'


@pytest.mark.parametrize("header, state, status_code", [
    ({'x-premoderation': 'true'}, True, 202),
    ({'x-premoderation': 'false'}, False, 200),
    ({}, False, 200)])
def test_post_comment_should_have_correct_premoderation_states(
        application, monkeypatch, header, state, status_code):
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
        assert ret_value['response']['premoderation'] is state


def test_user_comment_should_have_expected_structure(application):
    xml_str = """
        <item>
            <cid>1</cid>
            <title>[empty]</title>
            <description>&lt;p&gt;Ich praezisiere.&lt;/p&gt;</description>
            <pubDate>2015-11-17T10:39:50+00:00</pubDate>
            <cms_uniqueId>http://www.zeit.de/artikel/01</cms_uniqueId>
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
        'http://xml.zeit.de/artikel/01')

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


def test_user_comment_thread_should_have_expected_structure(
        application, testserver):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    thread = zeit.web.core.comments.get_user_comments(author)
    assert thread['uid'] == 172432
    assert thread['published_total'] == 570
    assert thread['page'] == 1
    assert thread['page_total'] == 95
    assert thread['sort'] == 'DESC'
    assert thread['rows'] == 6
    assert len(thread['comments']) == 6
