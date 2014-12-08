# -*- coding: utf-8 -*-
import lxml
import pytest

import selenium.webdriver


def test_footer_should_have_basic_structure(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/footer.html')
    html_str = tpl.render()
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('.footer__logo')) == 1, (
        'just one .footer__logo')

    assert len(html('.footer__logo__inner')) == 1, (
        'just one .footer__logo__inner')

    assert len(html('.footer__publisher')) == 1, (
        'just one .footer__publisher')

    assert len(html('.footer__publisher__inner')) == 1, (
        'just one .footer__publisher__inner')

    assert len(html('.footer__links')) == 1, (
        'just one .footer__links')

    assert len(html('.footer__links__inner')) == 1, (
        'just one .footer__links__inner')

    assert len(html('.footer__links__button')) == 1, (
        'just one .footer__links__button')


#integration tests

def test_footer_is_displayed(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)

    footer = driver.find_element_by_class_name(
        'footer')

    assert(footer.is_displayed()), (
        'footer isnt displayed')
