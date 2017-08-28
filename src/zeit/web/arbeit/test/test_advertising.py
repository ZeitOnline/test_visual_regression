# -*- coding: utf-8 -*-
import pyramid.testing

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.site


def test_zar_homepage_should_have_proper_ivw_script_integration(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)

    browser = testbrowser('/arbeit/slenderized-index')
    ivw = browser.cssselect('script[src="https://script.ioam.de/iam.js"]')
    assert len(ivw) == 1


def test_zar_adcontroller_head_code_is_present(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)

    browser = testbrowser('/arbeit/slenderized-index')

    assert '<!-- ad controller head start -->' in browser.contents
    assert '<!-- adcontroller load -->' in browser.contents
    assert '<!-- mandanten object -->' in browser.contents


def test_zar_adcontroller_adtags_are_present(testbrowser, monkeypatch):
    browser = testbrowser('/arbeit/slenderized-index')
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
    browser = testbrowser('/arbeit/slenderized-index')
    assert 'ad-desktop-7' in browser.contents
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)
    browser = testbrowser('/arbeit/slenderized-index')
    assert 'ad-desktop-8' in browser.contents


def test_zar_adcontroller_finalizer_is_present(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    browser = testbrowser('/arbeit/slenderized-index')
    assert 'AdController.finalize();' in browser.contents


def test_zar_adcontroller_js_var_isset(
        selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    driver = selenium_driver
    driver.get('%s/arbeit/slenderized-index' % testserver.url)

    adctrl = driver.execute_script("return typeof window.AdController")
    assert adctrl == "object"


def test_zar_adplaces_present_on_empty_cp(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True,
        'iqd_digital_transformation': True}.get)

    browser = testbrowser('/arbeit/slenderized-index')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-desktop-16')) == 1

    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


def test_zar_adplaces_present_on_cp(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)

    browser = testbrowser('/arbeit/index')
    assert len(browser.cssselect('#iqadtileOOP')) == 1
    assert len(browser.cssselect('#ad-desktop-1')) == 1
    assert len(browser.cssselect('#ad-desktop-2')) == 1
    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-desktop-4')) == 1
    assert len(browser.cssselect('#ad-desktop-5')) == 1
    assert len(browser.cssselect('#ad-desktop-16')) == 1

    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


def test_zar_adcontroller_values_return_values_on_article(
        application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/keywords')
    adcv = [
        ('$handle', 'artikel_trsf'),
        ('level2', u'arbeit'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,student,hochschule,auslandssemester,'
            'bafgantrag,praktikum,geschftfrmaanzge'),
        ('tma', '')]
    view = view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_zar_ads_are_rendered_on_articles_with_multiple_pages(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)
    selector = (
        '#ad-desktop-8', '#ad-desktop-4', '#ad-mobile-3', '#ad-mobile-4')

    browser = testbrowser('/arbeit/article/01-digitale-nomaden')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1
    assert len(browser.cssselect(selector[2])) == 1
    assert len(browser.cssselect(selector[3])) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-2')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1
    assert len(browser.cssselect(selector[2])) == 1
    assert len(browser.cssselect(selector[3])) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-3')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1
    assert len(browser.cssselect(selector[2])) == 1
    assert len(browser.cssselect(selector[3])) == 1

    browser = testbrowser(
        '/arbeit/article/01-digitale-nomaden/komplettansicht')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1
    assert len(browser.cssselect(selector[2])) == 1
    assert len(browser.cssselect(selector[3])) == 1


def test_zar_tile8_is_rendered_on_cp(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'iqd_digital_transformation': True}.get)
    browser = testbrowser('/arbeit/centerpage/adplace8')
    assert len(browser.cssselect('#ad-desktop-8')) == 1


def test_zar_desktop_ads_are_rendered_on_cp(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True,
        'iqd_digital_transformation': True}.get)
    browser = testbrowser('/arbeit/index')

    assert len(browser.cssselect('#ad-desktop-3')) == 1
    assert len(browser.cssselect('#ad-desktop-4')) == 1
    assert len(browser.cssselect('#ad-desktop-5')) == 1
    assert len(browser.cssselect('#ad-desktop-16')) == 1
