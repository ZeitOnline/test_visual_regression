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


def test_copyright_entries_are_rendered_correcly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/misc' % testserver.url)
    driver.find_elements_by_css_selector(
        ".js-image-copyright-footer")[0].click()
    # number of entries
    assert len(driver.find_elements_by_css_selector(
        '.image-copyright-footer__item')) == 3
    # copyright text itself
    copyright_label = driver.find_element_by_css_selector(
        '.image-copyright-footer__item > span').text
    assert u'© Karl Lagerfeld' in copyright_label
    # linked copyrights
    copyright_link = driver.find_element_by_css_selector(
        '.image-copyright-footer__item > a').get_attribute('href')
    assert 'http://www.photocase.de/milchhonig' in copyright_link


@pytest.fixture
def cp_factory(application, dummy_request):
    """A factory function to create dummy cp views with an `area` property
    that can be configured by providing an `area_getter` function. The `area`
    is decorated with zeit.web.register_copyrights.
    """
    def register_copyrights(func):
        def decorator(self):
            return self.register_copyrights(func(self))
        return decorator

    def wrapped(area_getter):
        cp = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-magazin/test-cp-legacy/test-cp-zmo')
        view_class = type('View', (
            zeit.web.magazin.view_centerpage.CenterpageLegacy,), {
                '_copyrights': {},
                'area': property(register_copyrights(area_getter))})
        view = view_class(cp, dummy_request)
        # Copyright registration needs to be triggered by accessing the
        # property at least once.
        view.area
        return view
    return wrapped


def test_teaser_list_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: s.context['lead'].values())
    # There are 8 unique teasers in the lead area, however, only 5 unique
    # teaser images are used.
    assert len(view._copyrights) == 5


def test_teaser_block_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: s.context['lead'].values()[0])
    assert len(view._copyrights) == 1


def test_auto_pilot_teaser_block_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: s.context['informatives'][1])
    assert len(view._copyrights) == 1


def test_teaser_bar_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: s.context['teaser-mosaic'].values()[0])
    # There are 6 unique teasers in the teaser mosaic, however, one image
    # is used twice.
    assert len(view._copyrights) == 5


def test_teaser_dict_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: {'foo': s.context['lead'][0]})
    assert len(view._copyrights) == 1


def test_nested_teaser_sequence_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: {'foo': {'bla': s.context['lead'][0]}})
    assert len(view._copyrights) == 1


def test_mixed_teaser_sequence_should_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: {'foo': s.context['lead'][0],
                                 'bla': s.context['informatives'][1],
                                 'meh': s.context['lead'].values()})
    assert len(view._copyrights) == 5  # 6 unique teaser images expected.


def test_empty_sequences_should_not_resolve_copyrights(cp_factory):
    view = cp_factory(lambda s: None)
    assert len(view._copyrights) == 0
    view = cp_factory(lambda s: [])
    assert len(view._copyrights) == 0
    view = cp_factory(lambda s: {})
    assert len(view._copyrights) == 0


def test_copyright_entries_are_rendered_correcly(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-legacy/test-cp-zmo')
    # 5 Unique teaser images with copyright information expected.
    assert len(browser.cssselect('.copyrights__entry')) == 5


def test_copyright_entry_images_are_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-legacy/test-cp-zmo')
    assert ('/zeit-magazin/2014/17/lamm-aubergine/'
            'lamm-aubergine-zmo-landscape-large.jpg') in browser.cssselect(
                '.copyrights__entry__image')[0].attrib['style']


def test_copyright_entry_labels_are_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-legacy/test-cp-zmo')
    assert u'© Jason Merritt/Getty Images' in browser.cssselect(
        'span.copyrights__entry__label')[2].text


def test_copyright_entry_links_are_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp-legacy/test-cp-zmo')
    assert 'http://www.photocase.de/milchhonig' in browser.cssselect(
        'span.copyrights__entry__label a')[0].attrib['href']


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


def test_nextread_teaser_images_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/header1')
    assert ('/zeit-magazin/2014/17/pistazienparfait/'
            'pistazienparfait-zmo-nextread.jpg') in browser.cssselect(
                'div.copyrights__image')[0].attrib['style']


def test_minimal_nextread_teaser_does_not_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/header2')
    assert all(['pistazienparfait-zmo-nextread.jpg' not in img.attrib['style']
               for img in browser.cssselect('div.copyrights__image')])


def test_missing_nextread_image_does_not_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/02')
    assert len(browser.cssselect('div.copyrights__image')) == 1


def test_inline_images_in_article_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/04')
    assert len(browser.cssselect('div.copyrights__image')) == 4


def test_copyright_entry_has_correct_label(testbrowser):
    browser = testbrowser('/artikel/04')
    labels = browser.cssselect('span.copyrights__label')
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/04')
    page = zeit.web.magazin.view_article.Article(article, mock.Mock()).pages[0]
    images = [i for i in page if isinstance(i, zeit.web.core.block.Image)]
    sorted_imgs = sorted(images, key=lambda i: i.copyright[0][0])
    for i in range(len(sorted_imgs)):
        assert sorted_imgs[i].copyright[0][0] == labels[i].text


def test_copyright_entry_has_correct_link(testbrowser):
    browser = testbrowser('/artikel/header5')
    assert (browser.cssselect('span.copyrights__label a')[0].attrib.get(
        'href') == 'http://foo.de')
    browser = testbrowser('/artikel/header6')
    assert not browser.cssselect('span.copyrights__label a')


def test_copyright_entry_has_correct_nofollow_attr(testbrowser):
    browser = testbrowser('/artikel/06')
    links = browser.cssselect('span.copyrights__label a')
    assert links[0].attrib.get('rel', '') == 'nofollow'
    assert not links[1].attrib.get('rel', False)


def test_inline_images_in_longform_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/06')
    assert len(browser.cssselect('div.copyrights__image')) == 3
    browser = testbrowser('/artikel/05')
    assert len(browser.cssselect('div.copyrights__image')) == 7


def test_longform_header_shows_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/05')
    assert any(['/exampleimages/artikel/05/01.jpg' in el.attrib['style'] for
               el in browser.cssselect('div.copyrights__image')])


def test_existing_header_image_shows_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/header2')
    assert '/exampleimages/artikel/traum.jpg' in browser.cssselect(
        'div.copyrights__image')[0].attrib['style']


def test_missing_header_image_does_not_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/artikel/header3')
    assert not browser.cssselect('div.copyrights__entry')


def test_gallery_image_should_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/galerien/bg-automesse-detroit-2014-usa')
    expected = (
        '/galerien/bg-automesse-detroit-2014-usa-bilder/'
        '02-shomei-tomatsu.jpg')
    assert expected in browser.cssselect(
        'div.copyrights__image')[0].attrib['style']


def test_only_gallery_images_with_cr_should_show_up_in_copyrights(testbrowser):
    browser = testbrowser('/galerien/bg-automesse-detroit-2014-usa')
    assert len(browser.cssselect('ul.copyrights__list li')) == 2


def test_centerpage_gracefully_skips_malformed_copyrights(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-2')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    group = 'http://xml.zeit.de/centerpage/katzencontent/'
    image = zeit.web.core.image.TeaserImage(
        zeit.cms.interfaces.ICMSContent(group),
        zeit.cms.interfaces.ICMSContent(group + 'katzencontent-180x101.jpg'))

    image.copyright, view._copyrights = [], {image.image_group: image}
    assert view.copyrights is not None
