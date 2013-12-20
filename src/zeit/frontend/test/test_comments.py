from pytest import fixture

@fixture
def xml_comment(agatho):
    return agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets').xpath('//comment')[0]


def test_agatho_collection_get(agatho):
    thread = agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    assert thread.xpath('comment_count')[0].text == '41'


def test_comment_as_json(xml_comment):
    from zeit.frontend.comments import comment_as_json
    json_comment = comment_as_json(xml_comment)
    assert json_comment['name'] == 'Skarsgard'


def test_get_entire_thread(dummy_request):
    from zeit.frontend.comments import thread
    thread_as_json = thread(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets', dummy_request)
    assert thread_as_json[0]['name'] == 'Skarsgard'
