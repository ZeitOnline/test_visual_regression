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


@pytest.fixture
def cp_factory(application):
    """A factory function to create dummy cp views with an `area` property
    that can be configured by providing an `area_getter` function. The `area`
    is decorated with zeit.web.register_copyrights.
    """
    def wrapped(area_getter):
        cp = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
        view = zeit.web.magazin.view_centerpage.Centerpage(cp, mock.Mock())

        view_class = type('View', (object,), {
            '_copyrights': {},
            'context': view.context,
            'area': property(zeit.web.register_copyrights(area_getter))}
        )
        view = view_class()
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


def test_copyright_entries_are_rendered_correcly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    # 5 Unique teaser images with copyright information expected.
    assert len(browser.cssselect('.copyrights__entry')) == 5


def test_copyright_entry_images_are_rendered_correctly(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert ('/zeit-magazin/2014/17/lamm-aubergine/'
            'lamm-aubergine-zmo-landscape-large.jpg') in browser.cssselect(
                '.copyrights__entry__image')[0].attrib['style']


def test_copyright_entry_labels_are_rendered_correctly(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert u'© Jason Merritt/Getty Images' in browser.cssselect(
        'span.copyrights__entry__label')[2].text


def test_copyright_entry_links_are_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert 'http://www.photocase.de/milchhonig' in browser.cssselect(
        'span.copyrights__entry__label a')[0].attrib['href']


def test_copyright_area_toggles_correctly(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert driver.find_elements_by_css_selector(
        '.copyrights')[0].value_of_css_property('display') == 'none'
    toggle = driver.find_elements_by_css_selector(".js-toggle-copyrights")[0]
    toggle.click()
    time.sleep(0.6)
    assert driver.find_elements_by_css_selector(
        '.copyrights')[0].value_of_css_property('display') == 'block'
    toggle.click()
    time.sleep(0.6)
    assert driver.find_elements_by_css_selector(
        '.copyrights')[0].value_of_css_property('display') == 'none'


def test_nextread_teaser_images_show_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    assert ('/zeit-magazin/2014/17/pistazienparfait/'
            'pistazienparfait-zmo-nextread.jpg') in browser.cssselect(
                'div.copyrights__entry__image')[0].attrib['style']


def test_minimal_nextread_teaser_does_not_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert all(['pistazienparfait-zmo-nextread.jpg' not in img.attrib['style']
               for img in browser.cssselect('div.copyrights__entry__image')])


def test_missing_nextread_image_does_not_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert len(browser.cssselect('div.copyrights__entry__image')) == 1


def test_inline_images_in_article_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert len(browser.cssselect('div.copyrights__entry__image')) == 4


def test_copyright_entry_has_correct_label(testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    labels = browser.cssselect('span.copyrights__entry__label')
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/04')
    page = zeit.web.magazin.view_article.Article(article, mock.Mock()).pages[0]
    images = [i for i in page if isinstance(i, zeit.web.core.block.Image)]
    sorted_imgs = sorted(images, key=lambda i: i.copyright[0][0])
    for i in range(len(sorted_imgs)):
        assert sorted_imgs[i].copyright[0][0] == labels[i].text


def test_copyright_entry_has_correct_link(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header5' % testserver.url)
    assert (browser.cssselect('span.copyrights__entry__label a')[0].attrib.get(
        'href') == 'http://foo.de')
    browser = testbrowser('%s/artikel/header6' % testserver.url)
    assert not browser.cssselect('span.copyrights__entry__label a')


def test_copyright_entry_has_correct_nofollow_attr(testserver, testbrowser):
    browser = testbrowser('%s/artikel/06' % testserver.url)
    links = browser.cssselect('span.copyrights__entry__label a')
    assert links[0].attrib.get('rel', '') == 'nofollow'
    assert not links[1].attrib.get('rel', False)


def test_inline_images_in_longform_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/06' % testserver.url)
    assert len(browser.cssselect('div.copyrights__entry__image')) == 3
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert len(browser.cssselect('div.copyrights__entry__image')) == 7


def test_longform_header_shows_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert any(['/exampleimages/artikel/05/01.jpg' in el.attrib['style'] for
               el in browser.cssselect('div.copyrights__entry__image')])


def test_existing_header_image_shows_up_in_copyrights(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert '/exampleimages/artikel/traum.jpg' in browser.cssselect(
        'div.copyrights__entry__image')[0].attrib['style']


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
        'div.copyrights__entry__image')[0].attrib['style']


def test_only_gallery_images_with_cr_should_show_up_in_copyrights(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url)
    assert len(browser.cssselect('ul.copyrights__list li')) == 1


def test_centerpage_gracefully_skips_malformed_copyrights(
        testserver, testbrowser):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-2')
    view = zeit.web.magazin.view_centerpage.Centerpage(cp, mock.Mock())

    group = 'http://xml.zeit.de/centerpage/katzencontent/'
    image = zeit.web.core.image.TeaserImage(
        zeit.cms.interfaces.ICMSContent(group),
        zeit.cms.interfaces.ICMSContent(group + 'katzencontent-180x101.jpg'))

    image.copyright, view._copyrights = [], {image.image_group: image}
    assert view.copyrights is not None
