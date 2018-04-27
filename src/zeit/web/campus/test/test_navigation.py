# coding: utf-8

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_nav_dropdowns_are_working_as_expected(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(1200, 980)
    driver.get('%s/campus/centerpage/teaser-topic-variant' % testserver.url)

    more = driver.find_element_by_class_name('nav__more-title')
    more_list = driver.find_element_by_class_name('nav__more-list')
    dropdown = driver.find_element_by_class_name('nav__tools-title')
    flyout = driver.find_element_by_class_name('header__flyout')

    # desktop
    more.click()
    assert more_list.is_displayed()
    dropdown.click()
    assert flyout.is_displayed()

    # mobile
    driver.set_window_size(320, 480)
    visible_more = expected_conditions.visibility_of(more)
    show_nav = driver.find_element_by_class_name('header__menu-link')
    show_nav.click()

    try:
        WebDriverWait(driver, 1).until(visible_more)
    except TimeoutException:
        assert False, 'Link must be visible'

    more.click()
    assert more_list.is_displayed()

    old_page = driver.find_element_by_tag_name('html')
    stale = expected_conditions.staleness_of(old_page)
    dropdown.click()
    try:
        WebDriverWait(driver, 20).until(stale)
        assert 'teaser-topic-variant' not in driver.current_url
    except TimeoutException:
        assert False, 'New page not visited'
