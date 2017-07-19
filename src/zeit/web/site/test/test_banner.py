# -*- coding: utf-8 -*-
import pyramid.testing

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.site


def test_banner_toggles_viewport_zoom(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/zeitonline')
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


def test_adcontroller_adtags_are_present(testbrowser, monkeypatch):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert 'ad-desktop-1' in browser.contents
    assert 'ad-desktop-2' in browser.contents
    assert 'ad-desktop-3' in browser.contents
    assert 'ad-mobile-1' in browser.contents
    assert 'ad-mobile-3' in browser.contents
    assert 'ad-mobile-4' in browser.contents
    assert 'ad-mobile-8' in browser.contents
    # adtile 7 will be renumbered to… 8
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': False}.get)
    browser = testbrowser('/zeit-online/slenderized-index')
    assert 'ad-desktop-7' in browser.contents
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)
    browser = testbrowser('/zeit-online/slenderized-index')
    assert 'ad-desktop-8' in browser.contents


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


def test_adplaces_present_before_video_stage(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    assert len(browser.cssselect('#ad-desktop-4')) == 1


def test_adplaces_present_before_buzzboard(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.view, 'is_hp', True)
    browser = testbrowser('/zeit-online/buzz-box')
    assert len(browser.cssselect('#ad-desktop-5')) == 1


def test_adplaces_present_on_zmo_cp(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True
    }.get)
    browser = testbrowser('/zeit-magazin/centerpage/lebensart')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


def test_adplaces_present_on_zco_cp(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True
    }.get)

    # test homepage
    browser = testbrowser('/campus/index')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1

    # test topic page with lead cinema teaser
    browser = testbrowser('/campus/centerpage/thema')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


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


def test_mobile_ad_place_right_behind_the_first_teaser(
        testbrowser, monkeypatch):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert browser.cssselect(
        '.main > div > div > article:nth-child(1) + div > script#ad-mobile-3 ')
    browser = testbrowser('/zeit-online/index-with-raw-on-top')
    assert browser.cssselect(
        '.main > div > div > article:nth-child(2) + div > script#ad-mobile-3 ')


def test_adplaces_have_banner_label_data_attribute(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True
    }.get)

    browser = testbrowser('/zeit-online/article/zeit')

    labelstring = "elem.setAttribute('data-banner-label', 'Anzeige');"

    assert labelstring not in browser.cssselect('#ad-desktop-1')[0].text
    assert labelstring not in browser.cssselect('#ad-desktop-2')[0].text
    assert labelstring in browser.cssselect('#ad-desktop-3')[0].text
    assert labelstring in browser.cssselect('#ad-desktop-5')[0].text
    assert labelstring in browser.cssselect('#ad-desktop-7')[0].text

    assert labelstring not in browser.cssselect('#ad-mobile-1')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-3')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-4')[0].text


def test_adplace8_has_banner_label_data_attribute(
        application, dummy_request, tplbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    browser = tplbrowser(
        'zeit.web.core:templates/inc/comments/thread.html', view=view)

    labelstring = "elem.setAttribute('data-banner-label', 'Anzeige');"

    assert labelstring in browser.cssselect('#ad-desktop-8')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-8')[0].text


def test_iqd_adtile2_should_not_be_inserted_on_small_screens(
        selenium_driver, testserver, monkeypatch):

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True
    }.get)

    driver = selenium_driver

    driver.set_window_size(920, 800)
    driver.get('%s/zeit-online/article/zeit/seite-2' % testserver.url)
    try:
        driver.find_element_by_css_selector('.ad-desktop--2')
        assert False
    except:
        assert True

    driver.set_window_size(1080, 800)
    driver.get('%s/zeit-online/article/zeit/seite-3' % testserver.url)
    assert driver.find_element_by_css_selector('.ad-desktop--2')
