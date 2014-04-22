import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_standard_gallery_is_there(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    selector = ".gallery"
    elem = driver.find_element_by_css_selector(selector)
    assert elem

def test_gallery_should_have_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper")))
        nextselector = ".bx-next"
        prevselector = ".bx-prev"
        # test navigation buttons
        nextbutton = driver.find_element_by_css_selector(nextselector)
        prevbutton = driver.find_element_by_css_selector(prevselector)
        assert nextbutton
        assert prevbutton
    except:
        print "Timeout Gallery Script"
        assert False

def test_gallery_buttons_are_clickable(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper")))
        onextselector = ".bx-overlay-next"
        oprevselector = ".bx-overlay-prev"
        onextbutton = driver.find_element_by_css_selector(onextselector)
        oprevbutton = driver.find_element_by_css_selector(oprevselector)
        onextbutton.click()
        oprevbutton.click()
    except:
        print "Timeout Gallery Script"
        assert False

def test_buttons_should_not_be_visible_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper")))
        driver.set_window_size(560, 900)
        elemNextDisplay = driver.execute_script('return $(".bx-overlay-next").css("display")')
        elemPrevDisplay = driver.execute_script('return $(".bx-overlay-next").css("display")')
        elemCaptionDisplay = driver.execute_script('return $(".figure__caption").css("display")')
        assert elemNextDisplay == "none"
        assert elemPrevDisplay == "none"
        assert elemCaptionDisplay == "none"
    except:
        print "Timeout Gallery Script"
        assert False

def test_buttons_should_be_visible_on_tap_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper")))
        driver.set_window_size(560, 900)
        figselector = ".inline-gallery .figure-full-width"
        figure = driver.find_element_by_css_selector(figselector)
        figure.click()
        elemNextDisplay = driver.execute_script('return $(".bx-overlay-next").css("display")')
        assert elemNextDisplay != "none"
    except:
        print "Timeout Gallery Script"
        assert False
