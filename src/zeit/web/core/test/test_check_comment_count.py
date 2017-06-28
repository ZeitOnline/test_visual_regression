# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_check_comment_count(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/check_teaser_comment_count'
               % testserver.url)

    # prevent testfail at first run
    presence_cp = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'main--centerpage'))

    try:
        WebDriverWait(driver, 3).until(presence_cp)
    except TimeoutException:
        assert False, 'CP must be visible'

    # check explicitly for absecnce of comments on non-zplus teasers
    # and vice versa
    classic_teasers = driver.find_elements_by_css_selector('.teaser-classic')
    assert len(classic_teasers) == 2
    try:
        classic_teasers[0].find_element_by_css_selector(
            '.teaser-classic__commentcount')
        assert False
    except NoSuchElementException:
        assert True

    try:
        classic_teasers[1].find_element_by_css_selector(
            '.teaser-classic__commentcount')
    except:
        assert False, 'Non zplus-teasers should have comment-count'
