# -*- coding: utf-8 -*-
import lxml
import mock
import pytest
import re


def test_footer_should_have_basic_structure(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/footer.html')
    html_str = tpl.render(view=mock.MagicMock())
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('.footer-logo')) == 1, (
        'just one .footer-logo')

    assert len(html('.footer-logo__image')) == 1, (
        'just one .footer-logo__image')

    assert len(html('.footer-logo__image')) == 1, (
        'just one .footer-logo__image')

    assert len(html('.footer-publisher')) == 1, (
        'just one .footer-publisher')

    assert len(html('.footer-links')) == 1, (
        'just one .footer-links')

    assert len(html('.footer-links__button')) == 1, (
        'just one .footer-links__button')


def test_footer_logo_macro_links_to_hp(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/footer_macro.tpl')

    request = mock.Mock()
    request.host = 'foo.bar'

    html_str = tpl.module.footer_logo(request)
    html = lxml.html.fromstring(html_str).cssselect

    assert html('a[href="http://foo.bar/index"]')[0] is not None, (
        'No link to zeit.de')


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
    driver.get('%s/zeit-online/index' % testserver.url)

    footer_button = driver.find_element_by_css_selector(
        '.footer-links__button a')

    footer_button.click()

    assert re.search(
        'http://.*/zeit-online/index',
        driver.current_url), ('footer button link is incorrect')


@pytest.mark.xfail(reason='Window resize and testing might interfere.')
def test_footer_publisher_structure_is_correct(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    footer_list = driver.find_elements_by_css_selector(
        '.footer-publisher__list')

    footer_inner = driver.find_elements_by_css_selector(
        '.footer-publisher__inner')

    footer_item = driver.find_elements_by_css_selector(
        '.footer-publisher__item')

    footer_link = driver.find_elements_by_css_selector(
        '.footer-publisher__link')

    footer_legal = driver.find_element_by_css_selector(
        '.footer-publisher__list--isfirst')

    footer_angebote = driver.find_element_by_css_selector(
        '.footer-publisher__list--issecond')

    footer_verlag = driver.find_element_by_css_selector(
        '.footer-publisher__list--islast')

    more_link = driver.find_element_by_class_name(
        'footer-publisher__more')

    driver.set_window_size(768, 1024)

    assert(len(footer_list) > 0), (
        'footer-publisher__list is not there')

    assert(len(footer_item) > 0), (
        'footer-publisher__item is not there')

    assert(len(footer_inner) > 0), (
        'footer-publisher__inner is not there')

    assert(len(footer_link) > 0), (
        'footer-publisher__link is not there')

    assert(footer_legal.is_displayed()), (
        'Legal Links in Footer arent displayed')

    assert(footer_angebote.is_displayed()), (
        'Angebote Links in Footer arent displayed')

    assert(footer_verlag.is_displayed()), (
        'Verlag Links in Footer arent displayed')

    assert(more_link.is_displayed()) is False, (
        'More link isnt displayed')

    # mobile
    driver.set_window_size(320, 480)

    assert(footer_legal.is_displayed()), (
        'Legal Links in Footer arent displayed')

    assert(footer_angebote.is_displayed() is False), (
        'Angebote Links in Footer are displayed')

    assert(footer_verlag.is_displayed() is False), (
        'Verlag Links in Footer are displayed')

    assert(more_link.is_displayed()), (
        'More link isnt displayed')


def test_footer_links_structure_is_correct(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    footer_list = driver.find_elements_by_css_selector(
        '.footer-links__list')

    footer_inner = driver.find_elements_by_css_selector(
        '.footer-links__inner')

    footer_item = driver.find_elements_by_css_selector(
        '.footer-links__item')

    footer_link = driver.find_elements_by_css_selector(
        '.footer-links__link')

    footer_first = driver.find_element_by_css_selector(
        '.footer-links__list--isfirst')

    footer_last = driver.find_element_by_css_selector(
        '.footer-links__list--islast')

    driver.set_window_size(768, 1024)

    assert(len(footer_list) > 0), (
        'footer-links__list is not there')

    assert(len(footer_item) > 0), (
        'footer-links__item is not there')

    assert(len(footer_inner) > 0), (
        'footer-links__inner is not there')

    assert(len(footer_link) > 0), (
        'footer-links__link is not there')

    assert(footer_first.is_displayed()), (
        'First Links in Footer arent displayed')

    assert(footer_last.is_displayed()), (
        'Last Links in Footer arent displayed')

    # mobile
    driver.set_window_size(320, 480)

    assert(footer_first.is_displayed() is False), (
        'First Links in Footer are displayed')

    assert(footer_last.is_displayed() is False), (
        'Last Links in Footer are displayed')


def test_more_button_works_as_expected(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    driver.set_window_size(320, 480)

    more_link = driver.find_element_by_class_name(
        'footer-publisher__more')

    publisher_first = driver.find_element_by_css_selector(
        '.footer-publisher__list--issecond')

    publisher_last = driver.find_element_by_css_selector(
        '.footer-publisher__list--islast')

    links_first = driver.find_element_by_css_selector(
        '.footer-links__list--isfirst')

    links_last = driver.find_element_by_css_selector(
        '.footer-links__list--islast')

    # open

    more_link.click()

    assert more_link.text == u'Schließen'

    assert(links_first.is_displayed()), (
        'First Links in Footer arent displayed')

    assert(links_last.is_displayed()), (
        'Last Links in Footer arent displayed')

    assert(publisher_first.is_displayed()), (
        'First Publisher in Footer isnt displayed')

    assert(publisher_last.is_displayed()), (
        'Last Publisher in Footer isnt displayed')

    # close

    more_link.click()

    assert more_link.text == u'Mehr'
