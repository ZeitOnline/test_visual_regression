import lxml.etree

import zeit.web.core.comments


def test_request_thread_should_respond(application):
    unique_id = ('/politik/deutschland/2013-07/wahlbeobachter-portraets/'
                 'wahlbeobachter-portraets')
    thread = zeit.web.core.comments.request_thread(unique_id)
    assert lxml.etree.fromstring(thread).xpath('comment_count')[0].text == '41'


def test_request_thread_should_respond_for_nonexistent(application):
    assert zeit.web.core.comments.request_thread('nosuchthread') is None


def test_comment_to_dict_should_parse_correctly(application):
    unique_id = ('/politik/deutschland/2013-07/wahlbeobachter-portraets/'
                 'wahlbeobachter-portraets')
    thread = zeit.web.core.comments.request_thread(unique_id)
    comment = lxml.etree.fromstring(thread).xpath('//comment')[0]
    json_comment = zeit.web.core.comments.comment_to_dict(comment)
    assert json_comment['name'] == 'Skarsgard'


def test_entire_thread_should_be_parsed(application):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination='foo', reverse=True)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


def test_paging_should_not_affect_comment_threads(application):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination='foo', reverse=True)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


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
