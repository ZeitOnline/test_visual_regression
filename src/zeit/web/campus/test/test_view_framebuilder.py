# -*- coding: utf-8 -*-
import zeit.web.core.application

import zope.component


def test_campus_framebuilder_accepts_banner_channel_parameter(
        selenium_driver, testserver):

    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules', 'iqd')
    driver = selenium_driver

    # avoid "diuquilon", which is added by JS for specific screen sizes
    driver.set_window_size(1200, 800)

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/homepage'))
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index_trsf' == driver.execute_script('return adcSiteInfo.$handle')
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
    assert 'artikel_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert '' == driver.execute_script('return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/four/my,keywords,in,channel'))
    assert 'four_trsf' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords,in,channel' == driver.execute_script(
        'return adcSiteInfo.keywords')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, '///homepage/my,keywords'))
    assert 'homepage_trsf' == driver.execute_script(
        'return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')
    assert 'my,keywords' == driver.execute_script(
        'return adcSiteInfo.keywords')


def test_campus_framebuilder_should_have_login_cut_mark(testbrowser):
    browser = testbrowser('/campus/framebuilder')
    assert 'start::cut_mark::login' in browser.contents
    assert 'end::cut_mark::login' in browser.contents


def test_campus_framebuilder_loads_slimmed_script_file(testbrowser):
    browser = testbrowser('/campus/framebuilder')
    scripts = browser.cssselect('body script')
    assert scripts[-1].get('src').endswith('/js/web.campus/frame.js')


def test_campus_framebuilder_uses_static_ssl_url(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['asset_prefix'] = 'https://static.zeit.de/static/latest/'
    browser = testbrowser('/campus/framebuilder')
    urls = browser.contents.count('https://static.zeit.de/static/latest/')
    assert urls == 5
    assert browser.xpath('//link[@rel="stylesheet"]/@href')[0].startswith(
        'https://static.zeit.de/static/latest/')
    assert browser.xpath('//link[@rel="shortcut icon"]/@href')[0].startswith(
        'https://static.zeit.de/static/latest/')
