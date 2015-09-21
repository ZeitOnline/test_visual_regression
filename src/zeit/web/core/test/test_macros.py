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


def test_esi_macro_should_produce_directive_depending_on_environment(
        jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    src = 'http://foo.com/bar'
    error_text = 'esi failed'
    html_for_wesgi = ('<!-- [esi-debug] src="{}" error_text="" -->'
                      '<esi:include src="{}" onerror="continue" />'
                      ).format(src, src)
    markup = tpl.module.insert_esi(src, is_dev=True)
    wesgi_string = ''
    for line in markup.splitlines():
        wesgi_string += line.strip()
    assert wesgi_string == html_for_wesgi

    html_for_varnish = ('<esi:remove>'
                        '<!-- [esi-debug] src="{}" error_text="{}" -->'
                        '</esi:remove>'
                        '<!--esi<esi:include src="{}" />-->'
                        ).format(src, error_text, src)
    markup = tpl.module.insert_esi(src, error_text)
    varnish_string = ''
    for line in markup.splitlines():
        varnish_string += line.strip()
    assert varnish_string == html_for_varnish
