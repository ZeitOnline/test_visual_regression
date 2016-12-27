# -*- coding: utf-8 -*-
import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    'article', [
        # thema
        ('.article-header__topic',
         'articleheader.thema...science'),
        # author
        ('.article-header__byline a',
         'articleheader.author.1_of_1..jochen_bittner'),
        # comment link
        ('.metadata__commentcount',
         'articleheader.comments...42_kommentare|#comments'),
        # intext
        ('.paragraph a',
         'articlebody.2.seite-1.paragraph.cyborgs|www.zeit.de/digital'),
        # toc
        ('.article-toc__link',
         'article-toc.page_1_of_10...2'),
        # nextread
        ('.nextread a',
         'articlebottom.editorial-nextread...area'),
    ])
def test_article_elements_provide_expected_id_for_webtrekk(
        selenium_driver, testserver, article):

    driver = selenium_driver
    driver.get('%s/campus/article/paginated#debug-clicktracking'
               % testserver.url)

    # prevent testfail at first run
    presence_art = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'main--article'))

    try:
        WebDriverWait(driver, 3).until(presence_art)
    except TimeoutException:
        assert False, 'Article must be visible'

    # don't test mobile and phablet here as some elements
    # aren't visible and we test the principle anyway

    # tablet
    driver.set_window_size(768, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    article_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('tablet.' + article[1] in track_str)

    # desktop
    driver.set_window_size(980, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    article_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + article[1] in track_str)
