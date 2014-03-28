import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_inline_gallery_is_there(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    selector = ".inline-gallery"
    elem = driver.find_element_by_css_selector(selector)
    assert elem

def test_inline_gallery_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    try:
      element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper")))
      nextselector = ".bx-next"
      prevselector = ".bx-prev"
      onextselector = ".bx-overlay-next"
      oprevselector = ".bx-overlay-prev"
      # test navigation buttons
      nextbutton = driver.find_element_by_css_selector(nextselector)
      prevbutton = driver.find_element_by_css_selector(prevselector)
      assert nextbutton
      assert prevbutton
      nextbutton.click()
      prevbutton.click()
      # test overlay buttons
      overlaynext = driver.find_element_by_css_selector(onextselector)
      elemOpacity = driver.execute_script('return $(".bx-overlay-next").css("opacity")')
      overlayprev = driver.find_element_by_css_selector(onextselector)
      assert overlaynext
      assert overlayprev
      overlaynext.click()
      elemOpacityLater = driver.execute_script('return $(".bx-overlay-next").css("opacity")')
      overlayprev.click()
      # opacity should have changed
      assert elemOpacity != elemOpacityLater
    except:
      print "Timeout Gallery Script"
      assert False
