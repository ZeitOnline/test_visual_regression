# -*- coding: utf-8 -*-


def test_campus_framebuilder_accepts_banner_channel_parameter(
        selenium_driver, testserver):

    driver = selenium_driver

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'one/two/three/homepage'))
    assert 'homepage' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'one' == driver.execute_script('return adcSiteInfo.level2')
    assert 'two' == driver.execute_script('return adcSiteInfo.level3')
    assert 'three' == driver.execute_script('return adcSiteInfo.level4')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'oans/zwoa//index'))
    assert 'index' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'oans' == driver.execute_script('return adcSiteInfo.level2')
    assert 'zwoa' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, 'eins'))
    assert '' == driver.execute_script('return adcSiteInfo.$handle')
    assert 'eins' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')

    driver.get('{}/campus/framebuilder?banner_channel={}'.format(
        testserver.url, '///artikel'))
    assert 'artikel' == driver.execute_script('return adcSiteInfo.$handle')
    assert '' == driver.execute_script('return adcSiteInfo.level2')
    assert '' == driver.execute_script('return adcSiteInfo.level3')
    assert '' == driver.execute_script('return adcSiteInfo.level4')

    driver.get('{}/campus/framebuilder'.format(testserver.url))
    assert 'undefined' == driver.execute_script('return typeof adcSiteInfo')
