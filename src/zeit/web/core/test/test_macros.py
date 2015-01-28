# -*- coding: utf-8 -*-
import mock


def test_macro_adplace_should_produce_markup(jinja2_env):
    # TODO: after importing banner.xml to the system
    # make multiple tests from this
    # with all standard banner
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    banner = {'name': 'superbanner',
              'tile': '1',
              'sizes': ['728x90'],
              'dcopt': 'ist',
              'label': 'anzeige',
              'noscript_width_height': ('728', '90'),
              'diuqilon': True,
              'min_width': 768}
    markup = ('document.write(\'<script src="http://ad.de.doubleclick.net/'
              'adj/zeitonline/zeitmz/centerpage;dcopt=ist;tile=1;\' + n_pbt '
              '+ \';sz=728x90;kw=iqadtile1,zeitonline,zeitmz,\' + iqd_TestKW '
              '+ window.diuqilon + \';ord=\' + IQD_varPack.ord + \'?" type='
              '"text/javascript"><\\/script>\');')
    view = mock.Mock()
    view.adwords = ['zeitonline', 'zeitmz']
    view.banner_channel = 'zeitmz/centerpage'
    lines = tpl.module.adplace(banner, view).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup in output


def test_adplace_middle_mobile_produces_html(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    elems = ['<div class="iqd-mobile-adplace iqd-mobile-adplace--middle">',
             '<div id="sas_13557"></div>']
    obj = mock.Mock()
    obj.tile = 7
    lines = tpl.module.adplace_middle_mobile(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_adplace_middle_mobile_dont_produces_html(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    lines = tpl.module.adplace_middle_mobile(False).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '' == output
