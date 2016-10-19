# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
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
    assert not browser.cssselect('div.inline-gallery')


def test_inline_gallery_buttons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "bx-wrapper")))
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
    assert image.xpath('.//@data-ratio')[0] == '1.77914110429'


def test_photocluster_has_expected_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/article/cluster-beispiel')
    cluster = browser.cssselect('.photocluster')[0]
    media = cluster.cssselect('.photocluster__media')
    images = cluster.cssselect('img')
    assert len(media) == 7
    assert len(images) == 7


def test_photocluster_has_expected_content(testbrowser):
    browser = testbrowser('/zeit-magazin/article/cluster-beispiel')
    images = browser.cssselect(".photocluster__media-item")

    assert images[0].attrib['src'].endswith(
        '/galerien/bg-automesse-detroit-2014-usa-bilder/'
        '462507429-540x304.jpg/imagegroup/original')
    assert images[5].attrib['src'].endswith(
        '/galerien/bg-automesse-detroit-2014-usa-bilder/'
        'VW_Dune-540x304.jpg/imagegroup/original')


def test_does_not_try_to_create_thumbnail(application):
    image = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/image'
        '/bertelsmann-infographic/piechart.png')
    zeit.content.image.interfaces.IPersistentThumbnail(image)
