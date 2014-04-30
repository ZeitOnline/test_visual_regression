import pytest
from zeit.frontend import view
from zeit.frontend import view_article
from zeit.frontend.banner import Place
import zeit.cms.interfaces
from zope.testbrowser.browser import Browser


def test_banner_place_should_be_serialized(testserver):
    place = Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
                              'label': '', 'min_width': 0, 'name': 'tile_1',
                              'noscript_width_height': ['728', '90'],
                              'sizes': ['728x90'], 'tile': 1}


def test_banner_place_should_raise_on_index_error(testserver):
    with pytest.raises(IndexError):
        Place(1, '123x456', True, label='')


def test_banner_list_should_be_sorted(testserver):
    tiles = [place.tile for place in zeit.frontend.banner.banner_list]
    assert sorted(tiles) == tiles


def test_banner_view_should_return_Place_if_tile_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert isinstance(article_view.banner(1), zeit.frontend.banner.Place)


def test_banner_view_should_return_None_if_tile_is_not_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert article_view.banner(999) is None


def test_banner_should_not_be_displayed_on_short_pages(testserver):
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__width_300">' \
        not in browser.contents


def test_banner_should_not_be_displayed_on_disabled_pages(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__width_300">' \
        not in browser.contents


def test_banner_view_should_be_displayed_on_odd_pages(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__on__article ad__width_300">' \
        in browser.contents
    browser = Browser('%s/artikel/03/seite-3' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__on__article ad__width_300">' \
        in browser.contents
    browser = Browser('%s/artikel/03/seite-7' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__on__article ad__width_300">' \
        in browser.contents
