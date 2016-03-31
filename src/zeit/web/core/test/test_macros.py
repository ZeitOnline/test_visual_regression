# -*- coding: utf-8 -*-
import zope.component

import zeit.web.core.interfaces


def test_adplace_middle_mobile_dont_produces_html(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    lines = tpl.module.adplace_middle_mobile(False).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '' == output


def test_esi_macro_should_produce_directive_depending_on_environment(
        jinja2_env):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    source = 'http://foo.com/bar'
    error_text = 'esi failed'

    conf['use_wesgi'] = True

    html_for_wesgi = ('<!-- [esi-debug] src="{0}" error_text="" -->'
                      '<esi:include src="{0}" onerror="continue" />'
                      ).format(source)
    markup = tpl.module.insert_esi(source)
    wesgi_string = ''
    for line in markup.splitlines():
        wesgi_string += line.strip()
    assert wesgi_string == html_for_wesgi

    conf['use_wesgi'] = False

    html_for_varnish = ('<esi:remove>'
                        '<!-- [esi-debug] src="{0}" error_text="{1}" -->'
                        '</esi:remove>'
                        '<!--esi<esi:include src="{0}" />-->'
                        ).format(source, error_text)
    markup = tpl.module.insert_esi(source, error_text)
    varnish_string = ''
    for line in markup.splitlines():
        varnish_string += line.strip()
    assert varnish_string == html_for_varnish
