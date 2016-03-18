# -*- coding: utf-8 -*-
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException


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
        cond = expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
        # test navigation buttons
        nextselector = ".bx-next"
        prevselector = ".bx-prev"
        nextbutton = driver.find_element_by_css_selector(nextselector)
        prevbutton = driver.find_element_by_css_selector(prevselector)
        assert nextbutton
        assert prevbutton


def test_gallery_buttons_are_clickable(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        cond = expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
        onextselector = ".bx-overlay-next"
        oprevselector = ".bx-overlay-prev"
        onextbutton = driver.find_element_by_css_selector(onextselector)
        oprevbutton = driver.find_element_by_css_selector(oprevselector)
        onextbutton.click()
        oprevbutton.click()


def test_buttons_should_not_be_visible_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(560, 900)
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    # This test is showing the last (or .bx-clone) slide, not the first one.
    # Not reproducible in the browser and unexplainable for now, since #400.
    # driver.save_screenshot("/tmp/buttons_should_not_be_visible_mobile.png")
    try:
        cond = expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
        bigbuttonprev = driver.find_element_by_css_selector(".bx-overlay-prev")
        bigbuttonnext = driver.find_element_by_css_selector(".bx-overlay-next")
        caption = driver.find_element_by_css_selector(".figure__caption")
        assert not bigbuttonprev.is_displayed()
        assert not bigbuttonnext.is_displayed()
        assert caption.is_displayed()


def test_buttons_should_be_visible_on_tap_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(560, 900)
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        cond = expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
        # TODO: this test fails without a window.resize event.
        # Findings:
        # needs resizeWindow() -> redrawSlider() -> setSlidePosition()
        # -> setPositionProperty() from jquery.bxslider.js (basically a reset)
        # both test_buttons_* tests are showing the last (or .bx-clone) slide,
        # not the first one. Unreproducible in the browser, introduced in #400.
        driver.set_window_size(1024, 768)
        # set window size for mobile again
        driver.set_window_size(560, 900)
        # driver.save_screenshot(
        #    "/tmp/test_buttons_should_be_visible_on_tap_mobile.png")
        figselector = ".js-gallery .slide:not(.bx-clone)"
        figure = driver.find_element_by_css_selector(figselector)
        figure.click()
        bigbuttonprev = driver.find_element_by_css_selector(".bx-overlay-prev")
        bigbuttonnext = driver.find_element_by_css_selector(".bx-overlay-next")
        assert bigbuttonprev.is_displayed()
        assert bigbuttonnext.is_displayed()


def test_gallery_with_supertitle_has_html_title(testbrowser):
    browser = testbrowser('/galerien/fs-desktop-schreibtisch-computer')
    assert ('<title>Desktop-Bilder: Das hab ich auf dem Schirm |'
            ' ZEITmagazin</title>'
            in browser.contents)


def test_gallery_without_supertitle_has_html_title(testbrowser):
    browser = testbrowser('/galerien/bg-automesse-detroit-2014-usa')
    assert ('<title>Automesse Detroit 2014 US-Hersteller | ZEITmagazin</title>'
            in browser.contents)


def test_standalone_gallery_uses_responsive_images_with_ratio(testbrowser):
    browser = testbrowser('/galerien/fs-desktop-schreibtisch-computer')
    image = browser.cssselect('.gallery .slide')[0]
    assert 'data-ratio="0.743405275779"' in etree.tostring(image)
