from pytest import fixture
from os import path

@fixture
def agatho():
    from zeit.frontend.comments import Agatho
    from zeit import frontend
    return Agatho(agatho_url=u'file://%s/' % path.join(path.dirname(path.abspath(frontend.__file__)), 'data', 'comments'))


def test_agatho_collection_get(agatho):
    thread = agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')
    assert thread.xpath('comment_count')[0].text == '41'
