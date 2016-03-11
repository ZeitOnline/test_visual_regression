# -*- coding: utf-8 -*-
import pyramid.testing
import pytest

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.site


def test_banner_toggles_viewport_zoom(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.banner_toggles('viewport_zoom') == 'tablet'


def test_homepage_should_have_proper_ivw_script_integration(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)

    browser = testbrowser('/zeit-online/slenderized-index')
    ivw = browser.cssselect('script[src="https://script.ioam.de/iam.js"]')
    assert len(ivw) == 1


def test_adcontroller_head_code_is_present(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)

    browser = testbrowser('/zeit-online/slenderized-index')

    assert '<!-- ad controller head start -->' in browser.contents
    assert '<!-- adcontroller load -->' in browser.contents
    assert '<!-- mandanten object -->' in browser.contents


def test_adcontroller_adtags_are_present(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')

    assert 'AdController.render(\'iqadtile1\');' in browser.contents
    assert 'AdController.render(\'iqadtile2\');' in browser.contents
    assert 'AdController.render(\'iqadtile3\');' in browser.contents
    assert 'AdController.render(\'iqadtile7\');' in browser.contents


def test_adcontroller_finanlizer_is_present(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    browser = testbrowser('/zeit-online/slenderized-index')

    assert 'AdController.finalize();' in browser.contents


def test_adcontroller_js_var_isset(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    adctrl = driver.execute_script("return typeof window.AdController")
    assert adctrl == "object"


def test_adplaces_present_on_pages(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)

    browser = testbrowser('/zeit-online/slenderized-index')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-desktop-7')) == 1

    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


def test_adplaces_present_on_home_page(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    assert len(browser.cssselect('#ad-desktop-12')) == 1


def test_iqd_sitebar_should_be_hidden_on_mobile(
        selenium_driver, testserver, monkeypatch):
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    script = """
        var el = document.createElement('div');
        el.id = 'iqdSitebar';
        el.textContent = 'NUR ZUM TESTEN';
        document.body.appendChild(el);"""
    driver.execute_script(script)
    elem = driver.find_element_by_css_selector('#iqdSitebar')
    driver.set_window_size(520, 800)
    assert not elem.is_displayed()
    driver.set_window_size(768, 800)
    assert elem.is_displayed()
