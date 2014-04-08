from pytest import fixture
from zeit.frontend.comments import get_thread
import requests

unique_id = u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets'

@fixture
def xml_comment(agatho):
    return agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets').xpath('//comment')[0]

@fixture
def xml_local_comment(agatho):
    return agatho.collection_get(u'http://localhost:8888/agatho/thread/artikel/03').xpath('//comment')[0]


def test_agatho_collection_get(agatho):
    thread = agatho.collection_get(unique_id)
    assert thread.xpath('comment_count')[0].text == '41'


def test_agatho_collection_get_for_nonexistent(agatho):
    assert agatho.collection_get(u'/nosuchthread') is None


def test_comment_as_json(xml_comment, testserver):
    r = requests.get(testserver.url + '/artikel/01')
    from zeit.frontend.comments import comment_as_json
    json_comment = comment_as_json(xml_comment, r)
    assert json_comment['name'] == 'claudiaE'


def test_get_entire_thread(dummy_request):
    thread_as_json = get_thread(unique_id, dummy_request)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41
