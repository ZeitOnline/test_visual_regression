# -*- coding: utf-8 -*-
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from zeit.frontend.test import Browser


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
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
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
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
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
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
        driver.set_window_size(560, 900)
        bigButtonPrev = driver.find_element_by_css_selector(".bx-overlay-prev")
        bigButtonNext = driver.find_element_by_css_selector(".bx-overlay-next")
        caption = driver.find_element_by_css_selector(".figure__caption")
        assert not bigButtonPrev.is_displayed()
        assert not bigButtonNext.is_displayed()
        assert not caption.is_displayed()
    except:
        print "Timeout Gallery Script"
        assert False


def test_buttons_should_be_visible_on_tap_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    try:
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
        # needed to fix a strange bug for consecutive execution of
        # test_buttons_should_not_be_visible_mobile() and this test
        # TODO: this test fails without a window.resize event. Why?
        # Findings: needs resizeWindow() -> redrawSlider()
        # -> setSlidePosition() -> setPositionProperty()
        # from jquery.bxslider.js
        driver.set_window_size(1024, 768)
        # set window size for mobile
        driver.set_window_size(560, 900)
        figselector = ".inline-gallery .figure-full-width:not(.bx-clone)"
        figure = driver.find_element_by_css_selector(figselector)
        figure.click()
        bigButtonPrev = driver.find_element_by_css_selector(".bx-overlay-prev")
        bigButtonNext = driver.find_element_by_css_selector(".bx-overlay-next")
        assert bigButtonPrev.is_displayed()
        assert bigButtonNext.is_displayed()
    except:
        print "Timeout Gallery Script"
        assert False


def test_standard_gallery_is_static(selenium_driver, testserver):
    gallery_url = ("%s/galerien/fs-desktop-schreibtisch-computer"
                   % testserver.url)
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get("%s?%s" % (gallery_url, "gallery=static"))
    try:
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-next"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        print "Timeout Gallery Script"
        assert False
    else:
        buttonNext = driver.find_element_by_css_selector(".bx-next")
        buttonNext.click()
        selector = ".inline-gallery figure:not(.bx-clone):nth-child(2)"
        slide = driver.find_element_by_css_selector(selector)
        assert driver.current_url == gallery_url + "?gallery=static&slide=2"
        assert slide.is_displayed()


def test_gallery_with_supertitle_has_html_title(browser, testserver):
    browser = Browser('%s/galerien/fs-desktop-schreibtisch-computer' % (
        testserver.url))
    assert '<title>Desktop-Bilder: Das hab ich auf dem Schirm</title>' \
        in browser.contents


def test_gallery_without_supertitle_has_html_title(browser, testserver):
    browser = Browser('%s/galerien/bg-automesse-detroit-2014-usa' % (
        testserver.url))
    assert '<title>Automesse Detroit 2014 US-Hersteller</title>' \
        in browser.contents


def test_standalone_gallery_uses_responsive_images_with_ratio(testserver):
    browser = Browser('%s/galerien/fs-desktop-schreibtisch-computer' % (
        testserver.url))
    image = browser.cssselect('div.inline-gallery div.scaled-image')[0]
    assert 'data-ratio="0.743405275779"' in etree.tostring(image)
