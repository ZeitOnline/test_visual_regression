# -*- coding: utf-8 -*-
import re
import mock

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_footer_should_have_basic_structure(tplbrowser, dummy_request):
    view = mock.MagicMock()
    view.package = 'zeit.web.site'
    select = tplbrowser(
        'zeit.web.site:templates/inc/footer.html',
        view=view, request=dummy_request).cssselect

    assert len(select('.footer-brand')) == 1, (
        'just one .footer-brand')

    assert len(select('.footer-brand__logo')) == 1, (
        'just one .footer-brand__logo')

    assert len(select('.footer-publisher')) == 1, (
        'just one .footer-publisher')

    assert len(select('.footer-links')) == 1, (
        'just one .footer-links')

    assert len(select('.footer-links__button')) == 1, (
        'just one .footer-links__button')


def test_footer_logo_links_to_hp(tplbrowser):
    view = mock.MagicMock()
    view.package = 'zeit.web.site'
    request = mock.Mock()
    request.route_url.return_value = 'http://foo.bar/'
    browser = tplbrowser(
        'zeit.web.site:templates/inc/footer.html',
        view=view, request=request)

    link = browser.cssselect('.footer-brand')[0]

    assert link.get('href') == 'http://foo.bar/index', (
        'footer logo should link to homepage')


# integration tests


def test_footer_is_displayed(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    footer = driver.find_element_by_class_name(
        'footer')

    assert(footer.is_displayed()), (
        'footer isnt displayed')


def test_footer_button_links_to_same_site(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    footer_button = driver.find_element_by_css_selector(
        '.footer-links__button a')

    footer_button.click()

    assert re.search(
        'http://.*/zeit-online/slenderized-index',
        driver.current_url), ('footer button link is incorrect')


def test_footer_publisher_structure_is_correct(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    footer = driver.find_element_by_tag_name('footer')

    footer_row = footer.find_elements_by_class_name('footer-publisher__row')
    footer_list = footer.find_elements_by_class_name('footer-publisher__list')
    footer_item = footer.find_elements_by_class_name('footer-publisher__item')
    footer_link = footer.find_elements_by_class_name('footer-publisher__link')

    fl_legal = footer_list[0]
    fl_angebote = footer_list[1]
    fl_verlag = footer_list[2]
    fl_more_link = footer.find_element_by_class_name('footer-publisher__more')

    driver.set_window_size(768, 1024)

    assert len(footer_list), 'footer-publisher__list must be present'
    assert len(footer_item), 'footer-publisher__item must be present'
    assert len(footer_row), 'footer-publisher__inner must be present'
    assert len(footer_link), 'footer-publisher__link must be present'

    assert fl_legal.is_displayed(), 'Legal footer links must be visible'
    assert fl_angebote.is_displayed(), 'Angebote footer links must be visible'
    assert fl_verlag.is_displayed(), 'Verlag footer links must be visible'
    assert not fl_more_link.is_displayed(), 'More link must be hidden'

    # mobile
    driver.set_window_size(320, 480)

    assert fl_legal.is_displayed(), 'Legal footer links must be visible'
    assert not fl_angebote.is_displayed(), (
        'Angebote footer links must be hidden')
    assert not fl_verlag.is_displayed(), 'Verlag footer links must be hidden'
    assert fl_more_link.is_displayed(), 'More link must be visible'


def test_footer_links_structure_is_correct(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    footer = driver.find_element_by_tag_name('footer')

    footer_row = footer.find_elements_by_class_name('footer-links__row')
    footer_list = footer.find_elements_by_class_name('footer-links__list')
    footer_item = footer.find_elements_by_class_name('footer-links__item')
    footer_link = footer.find_elements_by_class_name('footer-links__link')

    footer_first = footer_list[0]
    footer_last = footer_list[1]

    driver.set_window_size(768, 1024)

    assert len(footer_row), 'footer-links__row must be present'
    assert len(footer_list), 'footer-links__list must be present'
    assert len(footer_item), 'footer-links__item must be present'
    assert len(footer_link), 'footer-links__link must be present'
    assert footer_first.is_displayed(), 'First footer links must be visible'
    assert footer_last.is_displayed(), 'Last footer links must be visible'

    # mobile
    driver.set_window_size(320, 480)

    assert not footer_first.is_displayed(), (
        'First footer links must be hidden on mobile view')
    assert not footer_last.is_displayed(), (
        'Last footer links must be hidden on mobile view')


def test_more_button_works_as_expected(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    footer = driver.find_element_by_tag_name('footer')

    driver.set_window_size(320, 480)

    pub_list = footer.find_elements_by_class_name('footer-publisher__list')
    links_list = footer.find_elements_by_class_name('footer-links__list')
    more_link = footer.find_element_by_class_name('footer-publisher__more')

    pub_first = pub_list[1]
    pub_last = pub_list[2]
    links_first = links_list[0]
    links_last = links_list[1]

    # open

    more_link.click()
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, '.footer-publisher__list'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)
    assert more_link.text == u'Schließen'
    assert links_first.is_displayed(), 'First footer links must be visible'
    assert links_last.is_displayed(), 'Last footer links must be visible'
    assert pub_first.is_displayed(), 'First publisher links must be visible'
    assert pub_last.is_displayed(), 'Last publisher links must be visible'

    # close

    more_link.click()

    assert more_link.text == u'Mehr'
