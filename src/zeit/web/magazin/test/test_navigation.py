# -*- coding: utf-8 -*-
import pytest

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

screen_sizes = ((320, 480, True), (1024, 768, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_longform_navigation(testbrowser):
    browser = testbrowser('/artikel/05')
    header = browser.cssselect('.header')

    # there's exactly one navigation
    assert len(header) == 1

    # there is the logo
    assert header[0].cssselect('.header__logo')

    # sharing is available
    assert header[0].cssselect('.header__sharing')

    # sharing has two buttons
    assert len(header[0].cssselect('.header__link')) == 2

    # twitter and facebook icons are available
    assert len(header[0].cssselect('.header__sharing-icon')) == 2


def test_main_navigation(selenium_driver, testserver, screen_size):
    # run twice, once for small screens, once for large
    driver = selenium_driver

    # set to small size on first run
    small_screen = screen_size[2]
    driver.set_window_size(screen_size[0], screen_size[1])

    driver.get('%s/artikel/01' % testserver.url)

    header = driver.find_element_by_class_name('header')
    menu_icon = header.find_element_by_class_name('header__menu-link')
    navigation = header.find_element_by_id('navigation')
    logo = header.find_element_by_css_selector('.header__logo')

    ressorts = header.find_element_by_class_name('nav__ressorts')
    ressorts_links = ressorts.find_elements_by_tag_name('a')

    service = header.find_element_by_class_name('nav__service')
    service_button = service.find_element_by_xpath(
        '//a[@aria-controls="service-menu"]')
    service_list = service.find_element_by_class_name('nav__service-list')
    service_links = service_list.find_elements_by_tag_name('a')

    # navigation is visible
    assert header.is_displayed()

    # navigation is initially hidden on mobile, but visible on desktop
    if small_screen:
        assert menu_icon.is_displayed()
        assert not navigation.is_displayed()
    else:
        assert not menu_icon.is_displayed()
        assert navigation.is_displayed()

    # navigation can be opened by click
    if small_screen:
        menu_icon.click()
        # wait for animation
        try:
            WebDriverWait(driver, 1).until(
                expected_conditions.visibility_of(navigation))
        except TimeoutException:
            assert False, 'Navigation must be visible on click'
    else:
        assert navigation.is_displayed()

    # there is the logo visible
    assert logo.is_displayed()

    # wait for animation
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of(service_button))
    except TimeoutException:
        assert False, 'Service link must be visible'

    # service is present and can be opened
    assert service_button.is_displayed()
    assert not service_list.is_displayed()
    service_button.click()
    assert service_list.is_displayed()

    # service dropdown contains at least one link
    assert len(service_links) > 0

    # visible subressorts
    assert ressorts.is_displayed()
    assert len(ressorts_links) == 3
