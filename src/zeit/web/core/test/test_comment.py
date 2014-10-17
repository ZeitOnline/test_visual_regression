# -*- coding: utf-8 -*-
import urllib2

import pytest

from zeit.cms.interfaces import ID_NAMESPACE as NS


def test_comment_count_should_handle_missing_uid_param(
        comment_counter):
    with pytest.raises(urllib2.HTTPError):
        resp = comment_counter()
        assert resp.status == 412


def test_comment_count_should_handle_invalid_uid_param(
        comment_counter):
    with pytest.raises(urllib2.HTTPError):
        resp = comment_counter(unique_id='foo')
        assert resp.status == 412


def test_comment_count_should_return_expected_json_structure_for_cp_id(
        comment_counter):
    resp = comment_counter(unique_id=NS + 'zeit-online/main-teaser-setup')
    assert 'comment_count' in resp.json
    cc = resp.json['comment_count']
    assert cc[NS + 'zeit-online/cp-content/article-01'] == 103
    assert cc[NS + 'centerpage/article_image_asset'] == 125
    assert cc[NS + 'zeit-online/cp-content/article-02'] == 291


def test_comment_count_should_return_expected_json_structure_for_article_id(
        comment_counter):
    resp = comment_counter(unique_id=NS + 'artikel/01')
    assert 'comment_count' in resp.json
    cc = resp.json['comment_count']
    assert cc[NS + 'artikel/01'] == 129


def test_comment_count_should_fallback_to_zero_if_count_unavailable(
        comment_counter):
    resp = comment_counter(unique_id=NS + 'zeit-magazin/test-cp/test-cp-zmo-3')
    assert 'comment_count' in resp.json
    cc = resp.json['comment_count']
    assert cc[NS + 'zeit-magazin/test-cp/essen-geniessen-spargel-lamm'] == 0
