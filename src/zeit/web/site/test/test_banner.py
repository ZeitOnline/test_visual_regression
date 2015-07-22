# -*- coding: utf-8 -*-
import mock
import pytest

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.site


def is_adcontrolled(contents):
    return 'data-adDeliveryType="adcontroller"' in contents


# use this to enable third_party_modules
def tpm(me):
    return True


def test_banner_toggles_should_return_value(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.banner_toggles('testing_me') is False


def test_adcontroller_head_code_is_present(
        testserver, testbrowser, monkeypatch):

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert '<!-- ad controller head start -->' in browser.contents
    assert '<!-- adcontroller load -->' in browser.contents
    assert '<!-- mandanten object -->' in browser.contents


def test_adcontroller_adtags_are_present(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
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
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    if not is_adcontrolled(browser.contents):
        pytest.skip("not applicable due to oldschool ad configuration")

    assert 'AdController.finalize();' in browser.contents


def test_adcontroller_js_var_isset(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    try:
        selector = 'body[data-adDeliveryType="adcontroller"]'
        driver.find_element_by_css_selector(selector)
    except:
        pytest.skip("not applicable due to oldschool ad configuration")

    adctrl = driver.execute_script("return typeof window.AdController")
    assert adctrl == "object"


def test_article_ads_should_have_pagetype_modifier(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert 'ad-desktop--7-on-article' in browser.contents
