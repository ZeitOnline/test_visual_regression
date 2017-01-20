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
