# -*- coding: utf-8 -*-
import pytest

import zeit.web.core.application
import zeit.web.core.view


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_keyword_diuqilon(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)

    driver = selenium_driver
    driver.set_window_size(768, 1024)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    try:
        selector = 'body[data-ad-delivery-type="oldschool"]'
        driver.find_element_by_css_selector(selector)
    except:
        pytest.skip("not applicable due to new ad configuration")

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
def test_var_iqd_var_pack_isset(selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    try:
        selector = 'body[data-ad-delivery-type="oldschool"]'
        driver.find_element_by_css_selector(selector)
    except:
        pytest.skip("not applicable due to new ad configuration")

    varpack = driver.execute_script("return typeof window.IQD_varPack")
    assert varpack == "object"


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_tile2_not_ommitted_in_landscape(
        selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    script = 'return $(".ad-tile_2").find("script").size()'
    scripts = driver.execute_script(script)
    assert scripts > 1


@pytest.mark.xfail(reason='ad scripts may timeout')
def test_ad_content_ad_in_article(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert browser.cssselect('#iq-artikelanker')
