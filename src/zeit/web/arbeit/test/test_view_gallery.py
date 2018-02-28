def test_gallery_contains_basic_elements(testbrowser):
    browser = testbrowser('/arbeit/gallery/gallery')
    gallery = browser.cssselect('.gallery')[0]
    assert len(browser.cssselect('.byline'))
    assert len(browser.cssselect('.metadata'))
    assert len(browser.cssselect('.summary'))
    assert len(browser.cssselect('.gallery__description'))
    assert len(gallery.cssselect('.slide')) == 13
