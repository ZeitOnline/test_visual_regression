# -*- coding: utf-8 -*-
import zeit.cms.interfaces
from pytest import raises
from zope.testbrowser.browser import Browser


def test_product_gallery_should_render_according_to_type(testserver):
    browser = Browser('%s/produkte/katzen-cafe-london' % testserver.url)
    assert '<div class="product">' in browser.contents


def test_regular_gallery_should_render_according_to_type(testserver):
    browser = Browser(
        '%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url)
    assert '<div class="gallery">' in browser.contents


def test_product_view_object_has_images(testserver):
    product = 'http://xml.zeit.de/produkte/katzen-cafe-london'
    context = zeit.cms.interfaces.ICMSContent(product)
    assert len([context[i] for i in context]) == 7


def test_product_view_object_has_correct_type(testserver):
    product = 'http://xml.zeit.de/produkte/katzen-cafe-london'
    context = zeit.cms.interfaces.ICMSContent(product)
    assert context.type == 'zmo-product'
