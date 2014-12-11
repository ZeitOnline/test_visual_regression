# -*- coding: utf-8 -*-
import lxml
import re
import mock


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

    assert len(html('.icon-top-arrow')) == 1, (
        'just one .icon-top-arrow')


def test_footer_logo_macro_links_to_hp(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/footer_macro.tpl')
    html_str = tpl.module.footer_logo()
    html = lxml.html.fromstring(html_str).cssselect

    assert html('a[href="http://www.zeit.de/index"]')[0] is not None, (
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


def test_footer_elments_are_displayed_or_hidden(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    inner_link = driver.find_element_by_class_name(
        'footer-links__inner')

    # mobile
    driver.set_window_size(320, 480)

    assert(inner_link.is_displayed() is False)

    # higher than tablet
    driver.set_window_size(768, 1024)

    assert(inner_link.is_displayed())


def test_footer_publisher_structure_is_correct(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    footer_legal = driver.find_element_by_css_selector(
        '.footer-publisher__list--isfirst')

    footer_angebote = driver.find_element_by_css_selector(
        '.footer-publisher__list--issecond')

    footer_verlag = driver.find_element_by_css_selector(
        '.footer-publisher__list--islast')

    more_link = driver.find_element_by_class_name(
        'footer-publisher__more')

    assert(footer_legal.is_displayed()), (
        'Legal Links in Footer arent displayed')

    assert(footer_angebote.is_displayed()), (
        'Angebote Links in Footer arent displayed')

    assert(footer_verlag.is_displayed()), (
        'Verlag Links in Footer arent displayed')

    assert(more_link.is_displayed()) is False, (
        'More link isnt displayed')

    #mobile
    driver.set_window_size(320, 480)

    assert(footer_legal.is_displayed()), (
        'Legal Links in Footer arent displayed')

    assert(footer_angebote.is_displayed() is False), (
        'Angebote Links in Footer are displayed')

    assert(footer_verlag.is_displayed() is False), (
        'Verlag Links in Footer are displayed')

    assert(more_link.is_displayed()), (
        'More link isnt displayed')
