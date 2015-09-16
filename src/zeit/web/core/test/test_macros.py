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


def test_esi_macro_should_produce_different_directives(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    src = 'http://foo.com/bar'
    view = mock.Mock()

    html_for_wesgi = '<esi:include src="' + src + '" onerror="continue" />'
    view.is_dev_environment = True
    assert tpl.module.insert_esi(src, view).strip() == html_for_wesgi

    html_for_varnish =  '<esi:remove><!-- [esi-remove] esi failed -->'\
        '</esi:remove><!--esi<esi:include src="' + src + '" />-->'
    view.is_dev_environment = False
    __import__("pdb").set_trace()
    markup = tpl.module.insert_esi(src, view, 'esi failed')
    string = ''
    for line in markup.splitlines():
        string += line.strip()
    assert string == html_for_varnish
