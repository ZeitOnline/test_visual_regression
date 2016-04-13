# -*- coding: utf-8 -*-


def test_wrapper_functions_are_working(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp-legacy/test-cp-zmo' % testserver.url)

    # test window.wrapper object exists
    obj = driver.execute_script("return typeof(window.wrapper)")
    assert obj == "object", 'window.wrapper object doesnt exists'

    # test ressort
    ressort = driver.execute_script("return window.wrapper.getRessort()")
    assert ressort == "ZEITmagazin", 'Ressort is not ZEITmagazin'

    # test zmo header is hidden and spacer displayed
    driver.execute_script("window.wrapper.setHeaderMargin(111)")
    main_nav = driver.find_element_by_class_name('main-nav')
    spacer = driver.find_element_by_id('wrapper_spacer_header')
    assert main_nav.is_displayed() is False, 'Main nav is not hidden'
    assert spacer.is_displayed(), 'Spacer is not displayed'


def test_wrapper_functions_are_working_for_features(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/feature/feature_longform' % testserver.url)

    # test window.wrapper object exists
    obj = driver.execute_script("return typeof(window.wrapper)")
    assert obj == "object", 'window.wrapper object doesnt exists'

    # test ressort
    ressort = driver.execute_script("return window.wrapper.getRessort()")
    assert ressort == "Gesellschaft", 'Ressort is not Gesellschaft'

    # test zmo header is hidden and spacer displayed
    driver.execute_script("window.wrapper.setHeaderMargin(111)")
    main_nav = driver.find_element_by_class_name('main-nav')
    spacer = driver.find_element_by_id('wrapper_spacer_header')
    assert main_nav.is_displayed() is False, 'Main nav is not hidden'
    assert spacer.is_displayed(), 'Spacer is not displayed'


def test_clickcounter_produces_no_error(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)

    # test clickcount calls are without errors
    driver.execute_script("window.Zeit.clickCount.webtrekk(1)")
    driver.execute_script("window.Zeit.clickCount.ga(1)")
    driver.execute_script("window.Zeit.clickCount.ivw()")
    driver.execute_script("window.Zeit.clickCount.cc()")
    driver.execute_script("window.Zeit.clickCount.all(1)")

    errors = driver.execute_script('return window.jsErrors')

    assert not errors
