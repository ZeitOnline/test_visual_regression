# -*- coding: utf-8 -*-


def test_gallery_contains_basic_elements(testbrowser):
    browser = testbrowser('/zeit-magazin/leben/2015-02/magdalena-ruecken-fs')
    main = browser.cssselect('main')[0]
    gallery = main.cssselect('.gallery')[0]
    assert main.cssselect('header.header-article')
    assert main.cssselect('h1.headline')
    assert not main.cssselect('.header-article__subtitle')
    assert not main.cssselect('.header-article .meta')
    assert main.cssselect('.gallery__description')
    assert main.cssselect('.meta')
    assert len(gallery.cssselect('.slide')) == 10
