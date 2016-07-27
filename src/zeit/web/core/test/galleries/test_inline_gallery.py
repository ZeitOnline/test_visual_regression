# -*- coding: utf-8 -*-
import re

import lxml

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces


def test_inline_gallery_is_there(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert '<div class="inline-gallery"' in browser.contents


def test_nonexistent_gallery_is_ignored(testbrowser, workingcopy):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    with checked_out(article) as co:
        co.xml.body.division.gallery.set('href', 'http://xml.zeit.de/invalid')
    browser = testbrowser('/zeit-magazin/article/01')
    assert '<div class="inline-gallery"' not in browser.contents


def test_inline_gallery_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    try:
        cond = EC.presence_of_element_located((By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
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
        script = ('return window.getComputedStyle('
                  'document.querySelector(".bx-overlay-next")'
                  ').getPropertyValue("opacity")')
        elem_opacity = driver.execute_script(script)
        overlayprev = driver.find_element_by_css_selector(onextselector)
        assert overlaynext
        assert overlayprev
        overlaynext.click()
        script = ('return window.getComputedStyle('
                  'document.querySelector(".bx-overlay-next")'
                  ').getPropertyValue("opacity")')
        elem_opacity_later = driver.execute_script(script)
        overlayprev.click()
        # opacity should have changed
        assert elem_opacity != elem_opacity_later


def test_inline_gallery_uses_responsive_images_with_ratio(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    image = browser.cssselect('.inline-gallery .slide')[0]
    assert 'data-ratio="1.77914110429"' in lxml.etree.tostring(image)


def test_photocluster_has_expected_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/cluster-beispiel' % testserver.url)
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
    driver.get('%s/zeit-magazin/article/cluster-beispiel' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".photocluster")
    assert len(wrap) != 0
    for element in wrap:
        imgs = element.find_elements_by_tag_name("img")
        # first image
        assert re.search('http://.*/galerien/' +
                         'bg-automesse-detroit-2014-usa-bilder/' +
                         'bitblt-.*/' +
                         '462507429-540x304.jpg',
                         imgs[0].get_attribute("src"))
        # last image
        assert re.search('http://.*/galerien/' +
                         'bg-automesse-detroit-2014-usa-bilder/' +
                         'bitblt-.*/' +
                         'Audi_allroad-540x304.jpg',
                         imgs[6].get_attribute("src"))
