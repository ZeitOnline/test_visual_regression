# -*- coding: utf-8 -*-
import mock


def test_adplace_middle_mobile_dont_produces_html(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    lines = tpl.module.adplace_middle_mobile(False).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '' == output


def test_content_ad_place_produces_html(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    elem = '<div id="iq-artikelanker"></div>'
    view = mock.Mock()
    view.context.advertising_enabled = True
    lines = tpl.module.content_ad_article(view).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert elem in output
