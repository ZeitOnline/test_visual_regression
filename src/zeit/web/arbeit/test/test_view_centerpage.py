# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_zar_teaser_lead_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-lead').cssselect
    assert len(select('.teaser-lead')) == 4

    # byline only if it exists
    assert len(select('.teaser-lead__byline')) == 3

    # show fallback image if no image exists
    assert 1 == len(select(
        '.teaser-lead__media img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_teaser_duo_has_modifier(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-duo').cssselect
    assert len(select('.teaser-duo')) == 4
    assert len(select('.teaser-duo--bright')) == 2
    assert len(select('.teaser-duo--dark')) == 2


def test_zar_teaser_small_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-small').cssselect
    assert len(select('.teaser-small')) == 6
    assert len(select('.teaser-small__kicker')) == 6
    assert len(select('.teaser-small__title')) == 6
    assert len(select('.teaser-small__byline')) == 5
    assert len(select('.series-label')) == 2
    # Fallback image if article/teaser has none
    assert 1 == len(select(
        '.teaser-small img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_teaser_small_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/centerpage/teaser-small' % testserver.url)
    teaser_images = driver.find_elements_by_class_name('teaser-small__media')
    assert len(teaser_images) == 6
    for teaser_image in teaser_images:
        if '--force-mobile' in teaser_image.get_attribute('class'):
            assert teaser_image.is_displayed()
        else:
            assert teaser_image.is_displayed() is False


def test_zar_jobbox_dropdown_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/jobbox-dropdown').cssselect
    assert len(select('.jobbox-dropdown')) == 2
    assert len(select('.jobbox-dropdown__label')) == 2
    assert len(select('.jobbox-dropdown__dropdown')) == 2
    assert len(select('.jobbox-dropdown__button')) == 2


def test_zar_jobbox_dropdown_changes_link_on_select(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/arbeit/centerpage/jobbox-dropdown' % testserver.url)
    dropdown = driver.find_element_by_class_name('jobbox-dropdown__dropdown')
    dropdown.find_element_by_xpath("//option[text()='Kunst & Kultur']").click()

    button = driver.find_element_by_class_name('jobbox-dropdown__button')
    button_url = button.get_attribute('href')
    assert 'stellenmarkt/kultur_kunst' in button_url
    assert 'stellenmarkt.funktionsbox.streifen' in button_url


def test_zar_teaser_topic_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-topic').cssselect
    assert len(select('.teaser-topic')) == 1
    assert len(select('.teaser-topic-main')) == 1
    assert len(select('.teaser-topic-sub')) == 3

    assert len(select('.teaser-topic-main__button[href*="/thema/"]')) == 1

    # Fallback image if article/teaser has none
    assert 1 == len(select(
        '.teaser-topic img[src*="/zeit-magazin/default/teaser_image/"]'))


def test_zar_teaser_topic_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/centerpage/teaser-topic' % testserver.url)
    teaser_images = driver.find_elements_by_class_name(
        'teaser-topic-sub__media')
    assert len(teaser_images) == 3
    for teaser_image in teaser_images:
        assert teaser_image.is_displayed() is False


def test_zar_teasers_to_zplus_provide_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(600, 320)
    driver.get(url.format('/arbeit/centerpage/teasers-to-zplus-registration'))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.teaser-duo[data-zplus="zplus-register"]')))
    except TimeoutException:
        assert False, 'teaser with zplus must be present'

    link = driver.find_element_by_css_selector(
        '.teaser-duo--dark .teaser-duo__combined-link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'phablet.duo.2.2.teaser-duo-zplus-register.text|')


def test_zar_teaser_quote_has_correct_structure(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-quote').cssselect

    assert len(select('.teaser-quote')) == 4
    assert len(select('.teaser-quote--red')) == 2
    assert len(select('.teaser-quote--yellow')) == 2

    assert len(select('.teaser-quote__quotelink')) == 4
    assert len(select('.teaser-quote__text')) == 4
    assert len(select('.series-label')) == 3
    assert len(select('.teaser-quote__headingwrapper')) == 4
    assert len(select('.teaser-quote__heading')) == 4
    assert len(select('.teaser-quote__byline')) == 4
    assert len(select('.teaser-quote__kicker')) == 4
    assert len(select('.teaser-quote__kicker--leserartikel')) == 1
    assert len(select('.teaser-quote__title')) == 4

    def teaser(unique_id):
        return select('.teaser-quote[data-unique-id="{}"]'.format(unique_id))

    # Regular teaser has certain elements
    quote = teaser('http://xml.zeit.de/arbeit/teaser/quote')
    assert len(quote) == 1
    quote_linktitle = quote[0].cssselect(
        '.teaser-quote__quotelink')[0].get('title')
    assert quote_linktitle == 'Quoteteaser - Diese E-Mail sagt: Antworte!'

    # Images appear only for columns with an authorimage
    assert len(select('.teaser-quote__media')) == 1
    assert len(select('.teaser-quote__media.variant--square')) == 1
    column_quote = teaser('http://xml.zeit.de/arbeit/teaser/quote-column')
    assert len(column_quote) == 1
    column_quote_byline = column_quote[0].cssselect(
        '.teaser-quote__byline')[0].text
    assert 'Eine Kolumne von ' in column_quote_byline

    # Teasers to articles without a quote show the teaserText
    teaser_without_quote = teaser('http://xml.zeit.de/arbeit/teaser/serie')
    assert len(teaser_without_quote) == 1
    teaser_without_quote_text = teaser_without_quote[0].cssselect(
        '.teaser-quote__text')[0].text.strip()
    assert teaser_without_quote_text.startswith('Mit dem Jobwechsel')


def test_zar_topicpage_has_correct_structure(testbrowser, data_solr):
    # first page with handmade teasers
    select = testbrowser('/arbeit/centerpage/thema-opulent').cssselect
    assert 1 == len(select(
        '.cp-region--solo > .cp-area--solo > .topicpage-header + .markup'))
    assert len(select('.cp-area--duo')) == 2
    assert len(select('.teaser-duo')) == 1
    assert len(select('.jobbox-dropdown')) == 1
    assert len(select('.teaser-small')) == 3
    assert len(select('.cp-area--zar-ranking article.teaser-ranking')) == 10

    # second page without the handmade teasers
    select = testbrowser('/arbeit/centerpage/thema-opulent?p=2').cssselect
    assert len(select('.cp-region')) == 2
    assert len(select('.topicpage-header + .markup')) == 1
    assert len(select('.pager.pager--zar-ranking')) == 1
    # second page should be the current one
    assert len(select(
        '.pager__pages > .pager__page--current:nth-child(2)')) == 1


def test_zar_advertorial_cp_header_renders_correctly(testbrowser):
    select = testbrowser('/arbeit/centerpage/advertorial').cssselect
    assert len(select('.header-image')) == 1
    assert len(select('.header-advertorial__heading')) == 1
    assert len(select('.header-advertorial__kicker')) == 1
    assert len(select('.header-advertorial__title')) == 1
    assert len(select('.header__ad-label')) == 1
    assert len(select('.header-image__adlabel')) == 1


def test_zar_advertorial_has_markup_module(testbrowser):
    select = testbrowser('/arbeit/centerpage/advertorial').cssselect
    assert len(select('.markup')) == 1


def test_zar_advertorial_teaser_has_modifier(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-advertorial').cssselect
    assert len(select('.teaser-small--advertorial')) == 3
    assert len(select('.teaser-duo--advertorial')) == 2


def test_zar_topicpage_contains_required_structured_data(
        testbrowser, data_solr):
    data = testbrowser('/arbeit/centerpage/thema-automatic').structured_data()
    assert data['ItemList']['itemListElement']


def test_zar_centerpage_contains_no_itemlist(testbrowser, data_solr):
    data = testbrowser('/arbeit/index').structured_data()
    assert 'ItemList' not in data
