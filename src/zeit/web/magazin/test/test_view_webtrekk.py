# -*- coding: utf-8 -*-
import mock
import pyramid.decorator
import pyramid.interfaces
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_comment_form_provides_expected_webtrekk_string(
        selenium_driver, testserver, application):
    extensions = application.zeit_app.config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions)
    with mock.patch.dict(extensions.descriptors, {
            'user': pyramid.decorator.reify(lambda x: {
                'name': 'john.doe',
                'mail': 'test@example.org',
                'ssoid': 123,
                'has_community_data': True,
                'uid': 123,
            })}):
        driver = selenium_driver
        driver.set_window_size(1024, 768)
        driver.get('%s/zeit-magazin/article/01#debug-clicktracking'
                   % testserver.url)

        # prevent testfail on consecutive run
        try:
            WebDriverWait(driver, 3).until(
                expected_conditions.title_contains('Mei, is des traurig!'))
        except TimeoutException:
            assert False, 'page must be loaded'

        try:
            WebDriverWait(driver, 3).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, 'comment-form')))
        except TimeoutException:
            assert False, 'comment form must be present'

        form = driver.find_element_by_id('comment-form')

        # fill out comment
        form.find_element_by_tag_name('textarea').send_keys('Test')
        # submit form
        form.find_element_by_xpath('//input[@type="submit"]').click()

        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data == (
            'stationaer.comment_form.2.1..kommentar_senden|#comments')


def test_inline_gallery_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    pathname = '/zeit-magazin/article/inline-gallery'
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('{}{}#debug-clicktracking'.format(testserver.url, pathname))

    # prevent testfail on consecutive run
    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.title_contains('Wecker: Von allen gehasst'))
    except TimeoutException:
        assert False, 'page must be loaded'

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'bx-wrapper')))
    except TimeoutException:
        assert False, 'inline gallery must be present'

    driver.find_element_by_class_name('bx-prev').click()
    time.sleep(0.05)
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.4.seite-1.inline-gallery.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-next').click()
    time.sleep(0.05)
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.4.seite-1.inline-gallery.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-overlay-prev').click()
    time.sleep(0.05)
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.4.seite-1.inline-gallery.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-overlay-next').click()
    time.sleep(0.05)
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.4.seite-1.inline-gallery.ein_bild_vor')
    assert tracking_data.endswith(pathname)


def test_gallery_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    pathname = '/galerien/fs-desktop-schreibtisch-computer'
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('{}{}#debug-clicktracking'.format(testserver.url, pathname))

    # prevent testfail on consecutive run
    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.title_contains(
                'Das hab ich auf dem Magazin-Schirm'))
    except TimeoutException:
        assert False, 'page must be loaded'

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'bx-next')))
    except TimeoutException:
        assert False, 'gallery must be present'

    driver.find_element_by_class_name('bx-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.1.2.2.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.1.1.1.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-overlay-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.2.2.2.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-overlay-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.2.1.1.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)
