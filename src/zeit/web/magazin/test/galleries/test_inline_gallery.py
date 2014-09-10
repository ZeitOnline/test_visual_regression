# -*- coding: utf-8 -*-
import re
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from zeit.web.core.test import Browser


def test_inline_gallery_is_there(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<div class="inline-gallery"' in browser.contents


def test_inline_gallery_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    try:
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
        nextselector = ".bx-next"
        prevselector = ".bx-prev"
        onextselector = ".bx-overlay-next"
        # test navigation buttons
        nextbutton = driver.find_element_by_css_selector(nextselector)
        prevbutton = driver.find_element_by_css_selector(prevselector)
        assert nextbutton
        assert prevbutton
        nextbutton.click()
        prevbutton.click()
        # test overlay buttons
        overlaynext = driver.find_element_by_css_selector(onextselector)
        script = 'return $(".bx-overlay-next").css("opacity")'
        elemOpacity = driver.execute_script(script)
        overlayprev = driver.find_element_by_css_selector(onextselector)
        assert overlaynext
        assert overlayprev
        overlaynext.click()
        script = 'return $(".bx-overlay-next").css("opacity")'
        elemOpacityLater = driver.execute_script(script)
        overlayprev.click()
        # opacity should have changed
        assert elemOpacity != elemOpacityLater
    except:
        print "Timeout Gallery Script"
        assert False


def test_inline_gallery_uses_responsive_images_with_ratio(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    image = browser.cssselect('div.inline-gallery div.scaled-image')[0]
    assert 'data-ratio="1.77914110429"' in etree.tostring(image)


def test_photocluster_has_expected_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/cluster-beispiel' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".photocluster")
    assert len(wrap) != 0
    for element in wrap:
        img_wrap = element.find_elements_by_css_selector(
            ".photocluster__item")
        imgs = element.find_elements_by_tag_name(
            "img")
        assert len(img_wrap) == 7
        assert len(imgs) == 7


def test_photocluster_has_expected_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/cluster-beispiel' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".photocluster")
    assert len(wrap) != 0
    for element in wrap:
        imgs = element.find_elements_by_tag_name(
            "img")
        # first image
        assert re.search('http://.*/galerien/' +
                         'bg-automesse-detroit-2014-usa-bilder/' +
                         'bitblt-.*/' +
                         '462507429-540x304.jpg',
                         imgs[0].get_attribute("src"))
        # last image
        print imgs[6].get_attribute("src")
        assert re.search('http://.*/galerien/' +
                         'bg-automesse-detroit-2014-usa-bilder/' +
                         'bitblt-.*/' +
                         'Audi_allroad-540x304.jpg',
                         imgs[6].get_attribute("src"))
