from zope.testbrowser.browser import Browser


def test_product_gallery_should_render_according_to_type(testserver):
    url = '%s/produkte/katzen-cafe-london' % testserver.url
    gallery = Browser(url).contents
    assert '<div class="product">' in gallery


def test_regular_gallery_should_render_according_to_type(testserver):
    url = '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url
    gallery = Browser(url).contents
    assert '<div class="gallery">' in gallery
