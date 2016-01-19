# -*- coding: utf-8 -*-
import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.magazin
import zeit.web.core.sources


def is_adcontrolled(contents):
    return 'data-ad-delivery-type="adcontroller"' in contents


# use this to enable third_party_modules
def tpm(me):
    return True


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
    banner_list = list(zeit.web.core.sources.BANNER_SOURCE)
    tiles = [place.tile for place in banner_list]
    assert sorted(tiles) == tiles


def test_banner_view_should_return_Place_if_tile_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert isinstance(article_view.banner(1), zeit.web.core.banner.Place)


def test_banner_view_should_return_None_if_tile_is_not_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.banner(999) is None


def test_banner_toggles_viewport_zoom(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.banner_toggles('viewport_zoom') == 'tablet-landscape'


def test_banner_should_fallback_on_not_registered_banner_types(
        testserver, testbrowser):
    class Moep(zeit.web.magazin.view_article.Article):

        @property
        def type(self):
            return 'moep'

    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    moep_view = Moep(context, mock.MagicMock(return_value=''))
    expected = getattr(
        zeit.web.core.sources.IQD_MOBILE_IDS_SOURCE.ids[context.sub_ressort],
        'default')
    assert moep_view.iqd_mobile_settings == expected


def test_banner_should_not_be_displayed_on_short_pages(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert not browser.cssselect('#iqadtile4')


def test_banner_should_not_be_displayed_on_disabled_article(
        testserver, testbrowser):
    # test article with xml banner = no
    browser = testbrowser('%s/artikel/nobanner' % testserver.url)
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')
    # no mobile ad script
    assert not browser.cssselect('script[src*="js/libs/iqd/sasmobile.js"]')


def test_banner_should_not_be_displayed_on_disabled_cp(
        testserver, testbrowser):
    # centerpage without ads
    browser = testbrowser('%s/centerpage/index-without-ads' % testserver.url)
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')
    # no mobile ad script
    assert not browser.cssselect('script[src*="js/libs/iqd/sasmobile.js"]')


def test_banner_view_should_be_displayed_on_pages(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert browser.cssselect('#ad-desktop-7')
    assert browser.cssselect('#ad-desktop-8')
    browser = testbrowser('%s/artikel/03/seite-3' % testserver.url)
    assert browser.cssselect('#ad-desktop-7')
    browser = testbrowser('%s/artikel/03/seite-4' % testserver.url)
    assert browser.cssselect('#ad-desktop-7')
    browser = testbrowser('%s/artikel/03/seite-7' % testserver.url)
    assert browser.cssselect('#ad-desktop-7')


def test_banner_tile3_should_be_displayed_on_pages(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert browser.cssselect('#ad-desktop-3')
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert browser.cssselect('#ad-desktop-3')


def test_banner_view_should_be_displayed_on_succeeding_pages(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)
    assert not browser.cssselect('#iqadtile7')
    browser = testbrowser('%s/artikel/03/seite-5' % testserver.url)
    assert not browser.cssselect('#iqadtile7')
    browser = testbrowser('%s/artikel/03/seite-6' % testserver.url)
    assert not browser.cssselect('#iqadtile7')


def test_banner_should_be_displayed_on_article_when_banner_xml_is_missing(
        testserver, testbrowser, monkeypatch):

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'third_party_modules_is_enabled', tpm)

    # test article with xml banner is missing
    browser = testbrowser('%s/artikel/10' % testserver.url)
    # desktop ads
    assert browser.cssselect('script[id^="ad-desktop-"]')


def test_inject_banner_code_should_be_inserted_on_all_pages():
    total = 10
    pages = [mock.Mock() for i in xrange(total)]

    with mock.patch.object(zeit.web.core.article,
                           "_place_adtag_by_paragraph") as mock_method:
        with mock.patch.object(zeit.web.core.article,
                               "_place_content_ad_by_paragraph") as mock_meth:
            mock_method.return_value = True
            mock_meth.return_value = True
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

    monkeypatch.setattr(zeit.web.core.sources, "BANNER_SOURCE", mock.Mock())
    zeit.web.core.sources.BANNER_SOURCE = banner_list
    page = mock.Mock()
    setattr(page, "number", 1)
    p = zeit.web.core.block.Paragraph
    # we need at least three paragraphs to insert AFTER 1st (before 2nd)
    page.blocks = [p(mock.Mock()), p(mock.Mock()), p(mock.Mock())]
    zeit.web.core.article._place_adtag_by_paragraph(
        page, tile_list, possible_paragraphs)

    assert isinstance(page.blocks[1], mock.Mock)
