# -*- coding: utf-8 -*-
import zeit.web.core.application


def test_campus_framebuilder_accepts_banner_channel_parameter(
        selenium_driver, testserver, monkeypatch):

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'iqd': True}.get)
    driver = selenium_driver

    # avoid "diuquilon", which is added by JS for specific screen sizes
    driver.set_window_size(1200, 800)

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/homepage'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'oans' == driver.execute_script('return adcSiteInfo.level2')
    assert 'zwoa' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'eins'))
    assert '' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'eins' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, '///artikel'))
    assert 'artikel' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


def test_campus_framebuilder_should_have_login_cut_mark(testbrowser):
    browser = testbrowser('/campus/framebuilder')
    assert 'start::cut_mark::login' in browser.contents
    assert 'end::cut_mark::login' in browser.contents
