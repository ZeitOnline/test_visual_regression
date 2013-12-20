from pytest import fixture
from os import path

@fixture
def agatho():
    from zeit.frontend.comments import Agatho
    from zeit import frontend
    return Agatho(agatho_url=u'file://%s/' % path.join(path.dirname(path.abspath(frontend.__file__)), 'data', 'comments'))


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
