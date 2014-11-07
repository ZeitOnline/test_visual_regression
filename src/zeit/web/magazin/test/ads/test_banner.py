# -*- coding: utf-8 -*-
import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.magazin


def test_banner_place_should_be_serialized(testserver, testbrowser):
    place = zeit.web.core.banner.Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
                              'label': '', 'min_width': 0, 'name': 'tile_1',
                              'noscript_width_height': ['728', '90'],
                              'sizes': ['728x90'], 'tile': 1}


def test_banner_place_should_raise_on_index_error(testserver, testbrowser):
    with pytest.raises(IndexError):
        zeit.web.core.banner.Place(1, '123x456', True, label='')


def test_banner_list_should_be_sorted(testserver, testbrowser):
    tiles = [place.tile for place in zeit.web.core.banner.banner_list]
    assert sorted(tiles) == tiles


def test_banner_view_should_return_Place_if_tile_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert isinstance(article_view.banner(1), zeit.web.core.banner.Place)


def test_banner_view_should_return_None_if_tile_is_not_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.banner(999) is None


def test_banner_should_fallback_on_not_registered_banner_types(
        testserver, testbrowser):
    class Moep(zeit.web.magazin.view_article.Article):

        @property
        def type(self):
            return 'moep'

    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    moep_view = Moep(context, mock.MagicMock(return_value=''))
    expected = getattr(
        zeit.web.core.banner.iqd_mobile_ids[context.sub_ressort], 'default')
    assert moep_view.iqd_mobile_settings == expected


def test_banner_should_not_be_displayed_on_short_pages(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__width_300">' \
        not in browser.contents


def test_banner_should_not_be_displayed_on_disabled_article(
        testserver, testbrowser):
    # test article with xml banner = no
    browser = testbrowser('%s/artikel/02' % testserver.url)
    # no desktop ads
    assert not browser.cssselect('div[class*="ad__tile_"]')
    # no mobile ad script
    assert not browser.cssselect('script[src*="js/libs/iqd/sasmobile.js"]')


def test_banner_should_not_be_displayed_on_disabled_cp(
        testserver, testbrowser):
    # centerpage without ads
    browser = testbrowser('%s/centerpage/index-without-ads' % testserver.url)
    # no desktop ads
    assert not browser.cssselect('div[class*="ad__tile_"]')
    # no mobile ad script
    assert not browser.cssselect('script[src*="js/libs/iqd/sasmobile.js"]')


def test_banner_view_should_be_displayed_on_pages(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    assert ('<div id="iqadtile8" class="ad__tile_8 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = testbrowser('%s/artikel/03/seite-3' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = testbrowser('%s/artikel/03/seite-4' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = testbrowser('%s/artikel/03/seite-7' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents


def test_banner_tile3_should_be_displayed_on_pages(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert ('<div id="iqadtile3" class="ad__tile_3 ad__on__article '
            'ad__width_800 ad__min__768">') in browser.contents
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert ('<div id="iqadtile3" class="ad__tile_3 ad__on__centerpage '
            'ad__width_800 ad__min__768">') in browser.contents


def test_banner_view_should_be_displayed_on_succeeding_pages(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents
    browser = testbrowser('%s/artikel/03/seite-5' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents
    browser = testbrowser('%s/artikel/03/seite-6' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents


# Tests for articles
def test_banner_mobile_should_request_with_correct_data_in_article_mode(
        testserver, testbrowser):
    # Ressort mode-design
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert "sasmobile('32375/445612', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445612', 13557, sas_target);" in browser.contents
    assert "sasmobile('32375/445612', 13501, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_article_leben(
        testserver, testbrowser):
    # Ressort leben
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert "sasmobile('32375/445623', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445623', 13557, sas_target);" in browser.contents
    assert "sasmobile('32375/445623', 13501, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_article_essen(
        testserver, testbrowser):
    # Ressort essen-trinken
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert "sasmobile('32375/445618', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445618', 13557, sas_target);" in browser.contents
    assert "sasmobile('32375/445618', 13501, sas_target);" in browser.contents


def test_banner_mobile_should_fallback_for_articles_without_sub_ressort(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/09' % testserver.url)
    assert "sasmobile('" not in browser.contents


# Tests for cps
def test_banner_mobile_should_request_with_correct_data_in_cp_leben(
        testserver, testbrowser):
    # Ressort leben
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert "sasmobile('32375/445622', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445622', 13501, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_cp_mode(
        testserver, testbrowser):
    # Ressort mode-design
    browser = testbrowser('%s/centerpage/lebensart-2' % testserver.url)
    assert "sasmobile('32375/445611', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445611', 13501, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_cp_essen(
        testserver, testbrowser):
    # Ressort essen-trinken
    browser = testbrowser('%s/centerpage/lebensart-3' % testserver.url)
    assert "sasmobile('32375/445616', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445616', 13501, sas_target);" in browser.contents


# Tests for galleries
def test_banner_mobile_should_request_with_correct_data_in_gallery_mode(
        testserver, testbrowser):
    # Ressort mode-design
    browser = testbrowser(
        '%s/galerien/fs-desktop-schreibtisch-computer-3' % testserver.url)
    assert "sasmobile('32375/445613', 13500, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_gallery_essen(
        testserver, testbrowser):
    # Ressort essen-trinken
    browser = testbrowser(
        '%s/galerien/fs-desktop-schreibtisch-computer-2' % testserver.url)
    assert "sasmobile('32375/445619', 13500, sas_target);" in browser.contents


def test_banner_mobile_should_request_with_correct_data_in_gallery_leben(
        testserver, testbrowser):
    # Ressort leben
    browser = testbrowser(
        '%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    assert "sasmobile('32375/445624', 13500, sas_target);" in browser.contents


# Test for hp
def test_banner_mobile_should_request_with_correct_data_at_hp(
        testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    assert "sasmobile('32375/445608', 13500, sas_target);" in browser.contents
    assert "sasmobile('32375/445608', 13501, sas_target);" in browser.contents


def test_inject_banner_code_should_be_inserted_on_all_pages():
    total = 10
    pages = [mock.Mock() for i in xrange(total)]

    with mock.patch.object(zeit.web.core.article,
                           "_place_adtag_by_paragraph") as mock_method:
        mock_method.return_value = True
        zeit.web.core.article._inject_banner_code(pages, True, False)
        assert mock_method.call_count == total


def test_inject_banner_code_should_be_inserted_on_certain_pages():
    total = 10
    pages = [mock.Mock() for i in xrange(total)]

    with mock.patch.object(zeit.web.core.article,
                           "_place_adtag_by_paragraph") as mock_method:
        mock_method.return_value = True
        zeit.web.core.article._inject_banner_code(pages, True, True)
        assert mock_method.call_count == 1


def test_inject_banner_code_should_be_inserted_between_paragraphs(monkeypatch):
    tile_list = [0]
    possible_paragraphs = [1]
    banner_list = [mock.Mock()]

    monkeypatch.setattr(zeit.web.core.banner, "banner_list", banner_list)
    page = mock.Mock()
    p = zeit.web.core.block.Paragraph
    # we need at least three paragraphs to insert AFTER 1st (before 2nd)
    page.blocks = [p(mock.Mock()), p(mock.Mock()), p(mock.Mock())]
    zeit.web.core.article._place_adtag_by_paragraph(
        page, tile_list, possible_paragraphs)

    assert isinstance(page.blocks[1], mock.Mock)
