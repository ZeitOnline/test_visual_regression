# -*- coding: utf-8 -*-
import time


def test_copyright_entries_are_rendered_correcly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/misc' % testserver.url)
    driver.find_elements_by_css_selector(
        ".js-image-copyright-footer")[0].click()
    # number of entries
    assert len(driver.find_elements_by_css_selector(
        '.image-copyright-footer__item')) == 3
    # copyright text itself
    copyright_label = driver.find_element_by_css_selector(
        '.image-copyright-footer__item > span').text
    assert u'© Karl Lagerfeld' in copyright_label
    # linked copyrights
    copyright_link = driver.find_element_by_css_selector(
        '.image-copyright-footer__item > a').get_attribute('href')
    assert 'http://www.photocase.de/milchhonig' in copyright_link


def test_copyright_area_toggles_correctly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/misc' % testserver.url)
    assert driver.find_elements_by_css_selector(
        'script[id=image-copyright-template]')
    assert not driver.find_elements_by_css_selector('.image-copyright-footer')
    toggle = driver.find_elements_by_css_selector(
        ".js-image-copyright-footer")[0]
    toggle.click()
    time.sleep(0.6)
    assert driver.find_element_by_id('bildrechte').value_of_css_property(
        'display') == 'block'
    toggle.click()
    time.sleep(0.6)
    assert driver.find_element_by_id('bildrechte').value_of_css_property(
        'display') == 'none'
