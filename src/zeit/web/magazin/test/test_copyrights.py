# -*- coding: utf-8 -*-
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_copyright_entries_are_rendered_correcly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/misc' % testserver.url)
    driver.find_elements_by_css_selector(
        ".js-image-copyright-footer")[0].click()
    # number of entries
    assert len(driver.find_elements_by_css_selector(
        '.image-copyright-footer__item')) == 3
    # copyright text itself
    wait = WebDriverWait(driver, 10)
    span = wait.until(expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, '.image-copyright-footer__item > span')))
    label = driver.execute_script('return arguments[0].textContent', span)
    assert label.startswith(u'©')
    assert label.endswith(u'Karl Lagerfeld')
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
