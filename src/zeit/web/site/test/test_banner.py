# -*- coding: utf-8 -*-
import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.site


def is_adcontrolled(contents):
    return 'data-ad-delivery-type="adcontroller"' in contents


# use this to enable third_party_modules
def tpm(me):
    return True


def test_banner_toggles_viewport_zoom(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_toggles('viewport_zoom') == 'tablet'


def test_homepage_should_have_proper_ivw_script_integration(
        testbrowser, monkeypatch):

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    browser = testbrowser('/zeit-online/slenderized-index')
    ivw = browser.cssselect(
        'script[id="ivw-v2"]')
    assert len(ivw) == 1


def test_adcontroller_head_code_is_present(
        testserver, testbrowser, monkeypatch):

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    browser = testbrowser('%s/zeit-online/slenderized-index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert '<!-- ad controller head start -->' in browser.contents
    assert '<!-- adcontroller load -->' in browser.contents
    assert '<!-- mandanten object -->' in browser.contents


def test_adcontroller_adtags_are_present(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/slenderized-index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert 'AdController.render(\'iqadtile1\');' in browser.contents
    assert 'AdController.render(\'iqadtile2\');' in browser.contents
    assert 'AdController.render(\'iqadtile3\');' in browser.contents
    assert 'AdController.render(\'iqadtile7\');' in browser.contents


def test_adcontroller_finanlizer_is_present(
        testserver, testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)
    browser = testbrowser('%s/zeit-online/slenderized-index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert 'AdController.finalize();' in browser.contents


def test_adcontroller_js_var_isset(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    try:
        selector = 'body[data-ad-delivery-type="adcontroller"]'
        driver.find_element_by_css_selector(selector)
    except:
        pytest.skip("not applicable due to oldschool ad configuration")

    adctrl = driver.execute_script("return typeof window.AdController")
    assert adctrl == "object"


def test_adplaces_present_on_pages(testbrowser, monkeypatch):

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

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
