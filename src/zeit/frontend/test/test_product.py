# -*- coding: utf-8 -*-
import zeit.cms.interfaces
from pytest import raises
from selenium.common.exceptions import NoSuchElementException


def test_product_gallery_should_render_according_to_type(selenium_driver,
                                                         testserver):
    driver = selenium_driver
    driver.get('%s/produkte/katzen-cafe-london' % testserver.url)
    assert driver.find_element_by_class_name('product')
    with raises(NoSuchElementException):
        driver.find_element_by_class_name('gallery')


def test_regular_gallery_should_render_according_to_type(selenium_driver,
                                                         testserver):
    driver = selenium_driver
    driver.get('%s/galerien/bg-automesse-detroit-2014-usa' % testserver.url)
    assert driver.find_element_by_class_name('gallery')
    with raises(NoSuchElementException):
        driver.find_element_by_class_name('product')


def test_product_view_object_has_images(selenium_driver, testserver):
    product = 'http://xml.zeit.de/produkte/katzen-cafe-london'
    context = zeit.cms.interfaces.ICMSContent(product)
    assert len([context[i] for i in context]) == 7


def test_product_view_object_has_correct_type(selenium_driver, testserver):
    product = 'http://xml.zeit.de/produkte/katzen-cafe-london'
    context = zeit.cms.interfaces.ICMSContent(product)
    assert context.type == 'zmo-product'
