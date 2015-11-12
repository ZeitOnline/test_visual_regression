# -*- coding: utf-8 -*-

import zeit.cms.interfaces
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_zon_gallery_should_have_metadata(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.summary, .byline, .metadata')) == 3


def test_zon_gallery_should_have_no_pagination(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.pagination')) == 0


def test_zon_gallery_should_have_description(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery__description')) == 1


def test_zon_gallery_should_display_a_gallery(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery')) == 1


def test_zon_gallery_uses_svg_icons(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/gallery/biga_1' % testserver.url)
    try:
        cond = expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "bx-wrapper"))
        WebDriverWait(driver, 10).until(cond)
    except TimeoutException:
        assert False, 'Timeout gallery script'
    else:
        gallery = driver.find_element_by_css_selector(".gallery")
        svg_icons = gallery.find_elements_by_css_selector(".bx-arrow-icon")
        assert len(svg_icons) == 4, "svg arrow icons are missing"


def test_gallery_should_contain_veeseo_widget(testbrowser):
    browser = testbrowser('/zeit-online/gallery/biga_1')
    assert browser.cssselect('#veeseo-widget')
    assert browser.cssselect('.RA2VW2')
