import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_footer_is_there(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    selector = ".main-footer"
    elem = driver.find_element_by_css_selector(selector)
    assert elem

def test_footer_has_logo(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    main_footer = driver.find_elements_by_class_name('main-footer')[0]
    logo = main_footer.find_element_by_tag_name('img')
    assert(logo.is_displayed())