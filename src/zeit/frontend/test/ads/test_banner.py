import pytest
from zeit.frontend import view
from zeit.frontend import view_article
from zeit.frontend.banner import Place
import zeit.cms.interfaces


def test_place_should_be_serialized(testserver):
    place = Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
                              'label': '', 'min_width': 0, 'name': 'tile_1',
                              'noscript_width_height': ['728', '90'],
                              'sizes': ['728x90'], 'tile': 1}


def test_place_should_raise_on_index_error(testserver):
    with pytest.raises(IndexError):
        Place(1, '123x456', True, label='')


def test_view_banner_should_return_Place_if_tile_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert isinstance(article_view.banner(1), zeit.frontend.banner.Place)


def test_view_banner_should_return_None_if_tile_is_not_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert article_view.banner(999) is None
