# -*- coding: utf-8 -*-
import time

import mock
import pytest

import zeit.cms.interfaces

import zeit.web
import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.core.interfaces
import zeit.web.core.centerpage


def test_copyright_entries_are_rendered_correcly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-legacy/test-cp-zmo' % testserver.url)
    # 5 Unique teaser images with copyright information expected.
    assert len(browser.cssselect('.copyrights__entry')) == 5


def test_copyright_entry_images_are_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-legacy/test-cp-zmo')
    assert ('/zeit-magazin/2014/17/lamm-aubergine/'
            'lamm-aubergine-zmo-landscape-large.jpg') in browser.cssselect(
                '.copyrights__image')[0].attrib['style']


def test_copyright_entry_labels_are_rendered_correctly(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-legacy/test-cp-zmo' % testserver.url)
    assert u'© Jason Merritt/Getty Images' in browser.cssselect(
        'span.copyrights__label')[2].text


def test_copyright_entry_links_are_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-legacy/test-cp-zmo' % testserver.url)
    assert 'http://www.photocase.de/milchhonig' in browser.cssselect(
        'span.copyrights__label a')[0].attrib['href']


def test_copyright_area_toggles_correctly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/misc' % testserver.url)
    assert driver.find_elements_by_css_selector(
        'script[id=image-copyright-template]')
    assert not driver.find_elements_by_css_selector('.image-copyright-footer')
    toggle = driver.find_elements_by_css_selector(
        ".js-image-copyright-footer")[0]
    toggle.click()
    time.sleep(0.6)
    assert driver.find_element_by_id('bildrechte').value_of_css_property(
        'display') == 'block'
    toggle.click()
    time.sleep(0.6)
    assert driver.find_element_by_id('bildrechte').value_of_css_property(
        'display') == 'none'


def test_nextread_teaser_images_show_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    assert ('/zeit-magazin/2014/17/pistazienparfait/'
            'pistazienparfait-zmo-nextread.jpg') in browser.cssselect(
                'div.copyrights__image')[0].attrib['style']


def test_minimal_nextread_teaser_does_not_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert all(['pistazienparfait-zmo-nextread.jpg' not in img.attrib['style']
               for img in browser.cssselect('div.copyrights__image')])


def test_missing_nextread_image_does_not_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert len(browser.cssselect('div.copyrights__image')) == 1


def test_inline_images_in_article_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert len(browser.cssselect('div.copyrights__image')) == 4


def test_copyright_entry_has_correct_label(testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    labels = browser.cssselect('span.copyrights__label')
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/04')
    page = zeit.web.magazin.view_article.Article(article, mock.Mock()).pages[0]
    images = [i for i in page if isinstance(i, zeit.web.core.block.Image)]
    sorted_imgs = sorted(images, key=lambda i: i.copyright[0][0])
    for i in range(len(sorted_imgs)):
        assert sorted_imgs[i].copyright[0][0] == labels[i].text


def test_copyright_entry_has_correct_link(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header5' % testserver.url)
    assert (browser.cssselect('span.copyrights__label a')[0].attrib.get(
        'href') == 'http://foo.de')
    browser = testbrowser('%s/artikel/header6' % testserver.url)
    assert not browser.cssselect('span.copyrights__label a')


def test_copyright_entry_has_correct_nofollow_attr(testserver, testbrowser):
    browser = testbrowser('%s/artikel/06' % testserver.url)
    links = browser.cssselect('span.copyrights__label a')
    assert links[0].attrib.get('rel', '') == 'nofollow'
    assert not links[1].attrib.get('rel', False)


def test_inline_images_in_longform_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/06' % testserver.url)
    assert len(browser.cssselect('div.copyrights__image')) == 3
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert len(browser.cssselect('div.copyrights__image')) == 7


def test_longform_header_shows_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert any(['/exampleimages/artikel/05/01.jpg' in el.attrib['style'] for
               el in browser.cssselect('div.copyrights__image')])


def test_existing_header_image_shows_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert '/exampleimages/artikel/traum.jpg' in browser.cssselect(
        'div.copyrights__image')[0].attrib['style']


def test_missing_header_image_does_not_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header3' % testserver.url)
    assert not browser.cssselect('div.copyrights__entry')


def test_gallery_image_should_show_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser(
        '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url)
    expected = (
        '/galerien/bg-automesse-detroit-2014-usa-bilder/'
        '02-shomei-tomatsu.jpg')
    assert expected in browser.cssselect(
        'div.copyrights__image')[0].attrib['style']


def test_only_gallery_images_with_cr_should_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url)
    assert len(browser.cssselect('ul.copyrights__list li')) == 2


def test_centerpage_gracefully_skips_malformed_copyrights(
        testserver, testbrowser):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-2')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    group = 'http://xml.zeit.de/centerpage/katzencontent/'
    image = zeit.web.core.image.TeaserImage(
        zeit.cms.interfaces.ICMSContent(group),
        zeit.cms.interfaces.ICMSContent(group + 'katzencontent-180x101.jpg'))

    image.copyright, view._copyrights = [], {image.image_group: image}
    assert view.copyrights is not None
