# -*- coding: utf-8 -*-
import time

import mock
import pytest

import zeit.cms.interfaces

from zeit.frontend.test import Browser
from zeit.frontend.view_centerpage import register_copyrights
import zeit.frontend.view_centerpage


@pytest.fixture
def view_factory(application):
    """A factory function to create dummy view classes with an `area` property
    that can be configured by providing an `area_getter` function. The `area`
    is decorated with zeit.frontend.view_centerpage.register_copyrights.
    """
    def wrapped(area_getter):
        cp = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
        view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())

        view_class = type('View', (object,), {
            '_copyrights': {},
            'context': view.context,
            'area': property(register_copyrights(area_getter))}
        )
        view = view_class()
        # Copyright registration needs to be triggered by accessing the
        # property at least once.
        view.area
        return view
    return wrapped


def test_teaser_list_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: s.context['lead'].values())
    # There are 8 unique teasers in the lead area, however, only 5 unique
    # teaser images are used.
    assert len(view._copyrights) == 5


def test_teaser_block_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: s.context['lead'].values()[0])
    assert len(view._copyrights) == 1


def test_auto_pilot_teaser_block_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: s.context['informatives'][1])
    assert len(view._copyrights) == 1


def test_teaser_bar_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: s.context['teaser-mosaic'].values()[0])
    # There are 6 unique teasers in the teaser mosaic, however, one image
    # is used twice.
    assert len(view._copyrights) == 5


def test_teaser_dict_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: {'foo': s.context['lead'][0]})
    assert len(view._copyrights) == 1


def test_nested_teaser_sequence_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: {'foo': {'bla': s.context['lead'][0]}})
    assert len(view._copyrights) == 1


def test_mixed_teaser_sequence_should_resolve_copyrights(view_factory):
    view = view_factory(lambda s: {'foo': s.context['lead'][0],
                                   'bla': s.context['informatives'][1],
                                   'meh': s.context['lead'].values()})
    assert len(view._copyrights) == 6  # 6 unique teaser images expected.


def test_empty_sequences_should_not_resolve_copyrights(view_factory):
    view = view_factory(lambda s: None)
    assert len(view._copyrights) == 0
    view = view_factory(lambda s: [])
    assert len(view._copyrights) == 0
    view = view_factory(lambda s: {})
    assert len(view._copyrights) == 0


def test_copyright_entries_are_rendered_correcly(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    # 5 Unique teaser images with copyright information expected.
    assert len(browser.cssselect('.copyrights__entry')) == 5


def test_copyright_entry_images_are_rendered_correctly(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert ('/zeit-magazin/2014/17/lamm-aubergine/lamm-aubergine-zmo-upright'
            '.jpg') in browser.cssselect('.copyrights__entry__image'
                                         )[0].attrib['style']


def test_copyright_entry_labels_are_rendered_correctly(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert u'© Jason Merritt/Getty Images' in browser.cssselect(
        '.copyrights__entry__label')[2].text


def test_copyright_entry_links_are_rendered_correctly(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert 'http://www.photocase.de/milchhonig' in browser.cssselect(
        '.copyrights__entry__label a')[0].attrib['href']


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
