# -*- coding: utf-8 -*-


def test_gallery_contains_basic_elements(testbrowser):
    browser = testbrowser('/campus/gallery/gallery')
    gallery = browser.cssselect('.gallery')[0]
    assert len(browser.cssselect('.article-header__byline'))
    assert len(browser.cssselect('.article-header__metadata'))
    assert len(browser.cssselect('.article__summary'))
    assert len(browser.cssselect('.gallery__description'))
    assert len(gallery.cssselect('.slides')) == 13
