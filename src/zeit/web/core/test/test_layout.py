# -*- coding: utf-8 -*-


def test_wrapper_functions_are_working(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/index?app-content' % testserver.url)

    # test window.wrapper object exists
    obj = driver.execute_script("return typeof(window.wrapper)")
    assert obj == "object", 'window.wrapper object must exist'

    # test ressort
    ressort = driver.execute_script("return window.wrapper.getRessort()")
    assert ressort == "ZEITmagazin", 'Ressort must be ZEITmagazin'


def test_wrapper_functions_are_working_for_features(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/feature/feature_longform?app-content' % testserver.url)

    # test window.wrapper object exists
    obj = driver.execute_script("return typeof(window.wrapper)")
    assert obj == "object", 'window.wrapper object must exist'

    # test ressort
    ressort = driver.execute_script("return window.wrapper.getRessort()")
    assert ressort == "Gesellschaft", 'Ressort must be Gesellschaft'


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
