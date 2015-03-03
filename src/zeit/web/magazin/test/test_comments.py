import zeit.web.core.comments


def test_agatho_collection_get(agatho, monkeyagatho):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread = agatho.collection_get(unique_id)
    assert thread.xpath('comment_count')[0].text == '41'


def test_agatho_collection_get_for_nonexistent(agatho):
    assert agatho.collection_get('/nosuchthread') is None


def test_comment_as_dict(dummy_request, agatho, monkeyagatho):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    comment = agatho.collection_get(unique_id).xpath('//comment')[0]
    json_comment = zeit.web.core.comments.comment_as_dict(comment)
    assert json_comment['name'] == 'Skarsgard'


def test_get_entire_thread(dummy_request, monkeyagatho):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination=dummy_request.url, reverse=True)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


def test_paging_should_not_affect_comment_threads(
        dummy_request, monkeyagatho):
    dummy_request.path = 'http://xml.zeit.de/artikel/01/seite-2'
    dummy_request.traversed = ('artikel', '01')
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    thread_as_json = zeit.web.core.comments.get_thread(
        unique_id, destination=dummy_request.url, reverse=True)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41


def test_dict_with_article_paths_and_comment_counts_should_be_created(
        testserver):
    # if request on node-comment-statistics fails
    # nevertheless a dict should be return value:
    comment_count_dict = zeit.web.core.comments.comments_per_unique_id()
    assert isinstance(comment_count_dict, dict)
    # for test article path on existing node-comment-statistics
    # we expect the correct commentcount:
    comments_in_article = comment_count_dict['/centerpage/article_image_asset']
    assert comments_in_article == '125'
