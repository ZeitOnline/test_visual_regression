from zope.testbrowser.browser import Browser
import mock
import pytest
import requests

def test_centerpage_should_have_expected_markup(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert 'FOO' in browser.contents

def test_centerpage_has_correct_page_title(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    title = driver.title.strip()
    assert title == 'Lebensart - Mode, Essen und Trinken, Partnerschaft | ZEIT ONLINE'

def test_centerpage_has_correct_page_meta_description(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="description"]')
    teststring = 'Die Lust am Leben: Aktuelle Berichte, Ratgeber und...'
    assert meta_description_tag.get_attribute("content").strip() == teststring

def test_centerpage_has_correct_page_meta_keywords(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="keywords"]')
    teststring = u'ZEIT ONLINE, ZEIT MAGAZIN'
    assert meta_description_tag.get_attribute("content").strip() == teststring
