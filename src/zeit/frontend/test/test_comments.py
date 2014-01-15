from pytest import fixture
from zeit.frontend.comments import get_thread

unique_id = u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets'

@fixture
def xml_comment(agatho):
    return agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets').xpath('//comment')[0]


def test_agatho_collection_get(agatho):
    thread = agatho.collection_get(unique_id)
    assert thread.xpath('comment_count')[0].text == '41'


def test_agatho_collection_get_for_nonexistent(agatho):
    assert agatho.collection_get(u'/nosuchthread') is None


def test_comment_as_json(xml_comment):
    from zeit.frontend.comments import comment_as_json
    json_comment = comment_as_json(xml_comment)
    assert json_comment['name'] == 'Skarsgard'


def test_get_entire_thread(dummy_request):
    thread_as_json = get_thread(unique_id, dummy_request)
    assert thread_as_json['comments'][0]['name'] == 'Skarsgard'
    assert thread_as_json['comment_count'] == 41

def test_get_non_existent_thread(dummy_request):
    assert get_thread(u'/nosuchthread', dummy_request)['comment_count'] == 0
    assert get_thread(u'/nosuchthread', dummy_request)['comments'] == []


def test_get_entire_thread_via_rest(browser):
    thread_as_json = browser.get_json('http://example.com/-/comments/collection/artikel/01')
    assert thread_as_json.json['comments'][0]['name'] == 'Skarsgard'
    assert thread_as_json.json['comment_count'] == 41

