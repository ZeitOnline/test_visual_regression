# -*- coding: utf-8 -*-
from zeit.cms.interfaces import ID_NAMESPACE as NS

import zeit.web.core.comments


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
