# -*- coding: utf-8 -*-
import pytest

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.magazin


def test_banner_should_not_be_displayed_on_short_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-traum')
    assert not browser.cssselect('#iqadtile4')


def test_banner_should_not_be_displayed_on_disabled_article(testbrowser):
    # test article with xml banner = no
    browser = testbrowser('/zeit-magazin/article/nobanner')
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')


def test_banner_should_not_be_displayed_on_disabled_cp(testbrowser):
    # centerpage without ads
    browser = testbrowser('/zeit-magazin/centerpage/index-without-ads')
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')


def test_banner_tile8_should_appear_on_article_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.cssselect('#ad-desktop-8')
    browser = testbrowser('/zeit-magazin/article/03/seite-3')
    assert browser.cssselect('#ad-desktop-8')
    browser = testbrowser('/zeit-magazin/article/03/seite-4')
    assert browser.cssselect('#ad-desktop-8')
    browser = testbrowser('/zeit-magazin/article/03/seite-7')
    assert browser.cssselect('#ad-desktop-8')


def test_banner_tile3_should_be_displayed_on_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert browser.cssselect('#ad-desktop-3')
    browser = testbrowser('/zeit-magazin/centerpage/lebensart')
    assert browser.cssselect('#ad-desktop-3')


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_keyword_diuqilon(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)

    driver = selenium_driver
    driver.set_window_size(768, 1024)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)

    diuqilon = driver.execute_script("return window.diuqilon")
    # ipad
    assert diuqilon == ',diuqilon'
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    diuqilon = driver.execute_script("return window.diuqilon")
    # not ipad
    assert diuqilon == ''


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_viewport_is_resized_in_ipad_landscape(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)

    content = driver.execute_script("return document.getElementById('viewport"
                                    "-meta').getAttribute('content')")
    orientation = driver.execute_script("return Math.abs(window.orientation)")
    if orientation is 90:
        # ipad landscape
        assert 'width=1280' in content


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_viewport_is_not_resized_in_other_browser(
        selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)

    content = driver.execute_script("return document.getElementById('viewport"
                                    "-meta').getAttribute('content')")
    orientation = driver.execute_script("return Math.abs(window.orientation)")
    if orientation is not 90:
        # all other
        assert 'width=device-width' in content


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_tile2_not_ommitted_in_landscape(
        selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    script = 'return document.querySelectorAll(".ad-tile_2 script").length'
    scripts = driver.execute_script(script)
    assert scripts > 1


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_content_ad_in_article(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert browser.cssselect('#iq-artikelanker')


def test_adplace4_on_articles(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert len(browser.cssselect('#ad-desktop-4')) == 1


def test_adplace16_on_articles(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert len(browser.cssselect('#ad-desktop-16')) == 1


def test_zmo_adplace5_depends_on_ligatus_toggle_on(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True,
        'ligatus': True,
        'ligatus_on_magazin': True
    }.get)

    browser = testbrowser('/zeit-magazin/article/03')
    assert not browser.cssselect('#ad-desktop-5')


def test_zmo_adplace5_depends_on_ligatus_toggle_off(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True,
        'ligatus': False
    }.get)

    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.cssselect('#ad-desktop-5')
