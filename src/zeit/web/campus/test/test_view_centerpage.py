import re
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# import zeit.cms.interfaces

# import zeit.web.core.interfaces


def test_campus_navigation_should_present_flyout(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/campus/index' % testserver.url)
    link = driver.find_element_by_css_selector(
        '.nav__tools-title .nav__dropdown')
    link.click()
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'nav-flyout')))
    except TimeoutException:
        assert False, 'Navigation flyout not visible within 5 seconds'
    else:
        flyout = driver.find_elements_by_css_selector(
            '.nav-flyout__item')
        assert len(flyout) == 3
        link.click()
        try:
            WebDriverWait(driver, 5).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CLASS_NAME, 'nav-flyout')))
        except TimeoutException:
            assert False, 'Navigation flyout not hidden within 5 seconds'
        else:
            assert True


def test_campus_teaser_wide_small_should_not_display_its_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/campus/centerpage/teaser-wide-small' % testserver.url)
    teaser_image = driver.find_element_by_class_name(
        'teaser-wide-small__media-item')
    assert not teaser_image.is_displayed()

    driver.set_window_size(768, 800)
    assert teaser_image.is_displayed()


def test_campus_teaser_wide_small_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-wide-small').cssselect

    assert len(select('.teaser-wide-small')) == 3
    assert len(select('.teaser-wide-small__metadata')) == 3
    assert len(select('.teaser-wide-small__byline')) == 2
    assert len(select('.teaser-wide-small__content')) == 0

    byline = select('.teaser-wide-small__byline')[1]
    byline_text = re.sub(' +', ' ', byline.text.strip())
    assert byline_text == 'Von Viola Diem'


def test_campus_teaser_wide_large_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-wide-large').cssselect

    assert len(select('.teaser-wide-large')) == 2

    assert len(select(
        '.teaser-wide-large .teaser-wide-large__heading '
        '.teaser-wide-large__kicker')) == 2
    assert len(select(
        '.teaser-wide-large .teaser-wide-large__heading '
        '.teaser-wide-large__title')) == 2

    assert len(select('.teaser-wide-large__metadata')) == 2
    assert len(select('.teaser-wide-large__byline')) == 1
    assert len(select('.teaser-wide-large__content')) == 0


def test_campus_teaser_square_exists(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-square').cssselect
    assert len(select('.teaser-square')) == 4


def test_campus_teaser_lead_portrait_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-lead-portrait').cssselect
    assert len(select('.teaser-lead-portrait')) == 1
    assert len(select(
        '.teaser-lead-portrait .teaser-lead-portrait__content '
        '.teaser-lead-portrait__heading .teaser-lead-portrait__title')) == 1
    assert len(select('.teaser-lead-portrait__metadata')) == 1


def test_campus_teaser_lead_cinema_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-lead-cinema').cssselect
    assert len(select('.teaser-lead-cinema')) == 1
    assert len(select('.teaser-lead-cinema__content')) == 0
    assert len(select('.teaser-lead-cinema__metadata')) == 1


def test_campus_teaser_topic_is_rendered(testbrowser):
    select = testbrowser('/campus/centerpage/topic-teaser').cssselect
    assert len(select('.teaser-topic')) == 1
    assert len(select('.teaser-topic-main')) == 1
    assert len(select('.teaser-topic-item')) == 3
