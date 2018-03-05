# -*- coding: utf-8 -*-
import pyramid.testing

import zeit.cms.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.site


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
    assert 'ad-desktop-1' in browser.contents
    assert 'ad-desktop-2' in browser.contents
    assert 'ad-desktop-3' in browser.contents
    assert 'ad-desktop-8' in browser.contents
    assert 'ad-mobile-1' in browser.contents
    assert 'ad-mobile-3' in browser.contents
    assert 'ad-mobile-4' in browser.contents
    assert 'ad-mobile-8' in browser.contents


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
    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1


def test_adplaces_present_before_video_stage(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    assert len(browser.cssselect('#ad-desktop-4')) == 1


def test_adplaces_present_before_buzzboard(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.view.Base, 'is_hp', True)
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
    assert len(browser.cssselect('#ad-mobile-1')) == 1
    assert len(browser.cssselect('#ad-mobile-3')) == 1
    assert len(browser.cssselect('#ad-mobile-8')) == 1

    browser = testbrowser('/zeit-magazin/index')
    assert len(browser.cssselect('#ad-mobile-4')) == 1


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
    assert len(browser.cssselect('#ad-mobile-4')) == 1
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
        'iqd': True,
        'zon_admark': True
    }.get)

    browser = testbrowser('/zeit-online/article/zeit')

    labelstring = "elem.setAttribute('data-banner-label', 'Anzeige');"

    assert labelstring not in browser.cssselect('#ad-desktop-1')[0].text
    assert labelstring not in browser.cssselect('#ad-desktop-2')[0].text
    assert labelstring in browser.cssselect('#ad-desktop-3')[0].text
    assert labelstring in browser.cssselect('#ad-desktop-5')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-1')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-3')[0].text
    assert labelstring not in browser.cssselect('#ad-mobile-4')[0].text


def test_adplaces_have_no_banner_label_data_attribute(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True
    }.get)

    labelstring = "elem.setAttribute('data-banner-label', 'Anzeige');"

    browser = testbrowser('/zeit-online/article/zeit')
    assert labelstring not in browser.contents

    browser = testbrowser('/zeit-online/index')
    assert labelstring not in browser.contents


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


def test_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/infoboxartikel')
    adcv = [
        ('$handle', 'artikel_trsf'),
        ('level2', u'wissen'),
        ('level3', 'umwelt'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,affe,aggression,geschlechtsverkehr,'
            'schimpanse,sozialverhalten,studie'),
        ('tma', '')]
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_tile7_is_rendered_on_articles_with_multiple_pages(
        testbrowser):
    ad = '#ad-mobile-4'

    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(ad)) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    assert len(browser.cssselect(ad)) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    assert len(browser.cssselect(ad)) == 1


def test_adplace_P4_is_rendered_on_articles_with_multiple_pages(
        testbrowser):
    selector = ('#ad-desktop-8', '#ad-mobile-4')

    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1


def test_tiles8_9_are_rendered_on_articles_with_multiple_pages_on_onepage_view(
        testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    assert len(browser.cssselect('#ad-desktop-8')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1


def test_article_ad8_should_have_pagetype_modifier(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-8')) == 1
    assert 'ad-desktop--8-on-article' in browser.contents


def test_adcontroller_values_return_values_on_hp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    adcv = [
        ('$handle', 'homepage_trsf'),
        ('level2', 'homepage'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_adcontroller_values_return_values_on_cp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    adcv = [
        ('$handle', 'index_trsf'),
        ('level2', 'politik'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,sashawaltz,interpol'),
        ('tma', '')]
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_video_page_adcontroller8_code_is_embedded(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    assert len(browser.cssselect('#ad-desktop-8')) == 1


def test_tile8_is_rendered_on_correct_position(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    tile8_on_first_position = browser.cssselect(
        '.cp-area--minor > div:first-child > script[id="ad-desktop-8"]')
    tile8_is_present = browser.cssselect(
        '.cp-area--minor > div > script[id="ad-desktop-8"]')

    assert not tile8_on_first_position, (
        'There should be no ad tile 8 on the first position.')
    assert tile8_is_present, (
        'Ad tile 8 is not present.')


def test_tile8_for_fullwidth_is_rendered_on_correct_position(
        testbrowser):
    browser = testbrowser('/zeit-online/index')
    tile8_on_first_position = browser.cssselect(
        '.cp-area--minor > div:first-child > script[id="ad-desktop-8"]')
    assert tile8_on_first_position, (
        'Ad tile 8 is not present on first position.')


def test_adplace4_on_articles(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-4')) == 1


def test_adplace16_on_articles(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-16')) == 1


def test_iqd_adtile8_on_article_new_placement(testbrowser):
    ps = '.article-page[data-page-number="1"] p'
    divs = '.article-page[data-page-number="1"] script[id^="ad-desktop"]'
    # article with original placement after p1
    browser = testbrowser('/zeit-online/article/01')
    body = browser.cssselect('{},{}'.format(ps, divs))
    assert body[1].cssselect('script')[0].get('id') == 'ad-desktop-8'


def test_iqd_adtile8_on_article_new_placement_alternative(
        testbrowser):
    ps = '.article-page[data-page-number="1"] p'
    divs = '.article-page[data-page-number="1"] script[id^="ad-desktop"]'
    # article with alternate placement after p2
    browser = testbrowser('/zeit-magazin/article/01')
    body = browser.cssselect('{},{}'.format(ps, divs))
    assert body[2].cssselect('script')[0].get('id') == 'ad-desktop-8'


def test_p5_not_displayed_when_there_are_no_comments(testbrowser):
    browser = testbrowser('/zeit-online/article/quiz')
    assert not browser.cssselect('#ad-desktop-5')
