import pytest

def test_inline_gallery_is_there(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    selector = ".inline-gallery"
    elem = driver.find_element_by_css_selector(selector)
    assert elem
