# -*- coding: utf-8 -*-
import lxml
import pytest

import selenium.webdriver


def test_footer_should_have_basic_structure(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/footer.html')
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('.footer')) == 1, (
        'just one .footer should be present')

    assert len(html('.footer > .footer__logo')) == 1, (
        'just one .footer__logo')

    assert len(html('.footer > .footer__logo__inner')) == 1, (
        'just one .footer__logo__inner')

    assert len(html('.footer > .footer__publisher')) == 1, (
        'just one .footer__publisher')

    assert len(html('.footer > .footer__publisher__inner')) == 1, (
        'just one .footer__publisher__inner')

    assert len(html('.footer > .footer__links')) == 1, (
        'just one .footer__links')

    assert len(html('.footer > .footer__links__inner')) == 1, (
        'just one .footer__links__inner')

    assert len(html('.footer > .footer__links__button')) == 1, (
        'just one .footer__links__button')
