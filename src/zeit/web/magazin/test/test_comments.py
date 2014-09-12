# -*- coding: utf-8 -*-
from pytest import fixture


unique_id = u'http://xml.zeit.de/politik/deutschland/'\
    '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets'


@fixture
def xml_comment(agatho):
    return agatho.collection_get(
        u'http://xml.zeit.de/politik/deutschland/2013-07/'
        'wahlbeobachter-portraets/'
        'wahlbeobachter-portraets').xpath('//comment')[0]


@fixture
def xml_local_comment(agatho):
    return agatho.collection_get(
        u'http://localhost:8888/agatho/'
        'thread/artikel/03').xpath('//comment')[0]


def test_agatho_collection_get(agatho, monkeyagatho):
    thread = agatho.collection_get(unique_id)
    assert thread.xpath('comment_count')[0].text == '41'


def test_agatho_collection_get_for_nonexistent(agatho):
    assert agatho.collection_get(u'/nosuchthread') is None


def test_comment_as_dict(dummy_request, agatho, monkeyagatho):
    from zeit.web.core.comments import comment_as_dict
    comment = xml_comment(agatho)
    json_comment = comment_as_dict(comment, dummy_request)
    assert json_comment['name'] == 'claudiaE'


def test_get_entire_thread(dummy_request, monkeyagatho):
    from zeit.web.core.comments import get_thread
    thread_as_json = get_thread(unique_id, dummy_request)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


def test_paging_should_not_affect_comment_threads(
        dummy_request, monkeyagatho):
    from zeit.web.core.comments import get_thread
    dummy_request.path = 'http://xml.zeit.de/artikel/01/seite-2'
    dummy_request.traversed = ('artikel', '01')
    thread_as_json = get_thread(unique_id, dummy_request)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


def test_dict_with_article_paths_and_comment_counts_should_be_created(
        testserver):
    from zeit.web.core.comments import comments_per_unique_id
    # if request on node-comment-statistics fails
    # nevertheless a dict should be return value:
    stats_path = 'community/node-comment-statistics.xml'
    comment_count_dict = comments_per_unique_id(stats_path)
    assert isinstance(comment_count_dict, dict)
    # for test article path on existing node-comment-statistics
    # we expect the correct commentcount:
    comments_in_article = comment_count_dict['/centerpage/article_image_asset']
    assert comments_in_article == '22'
