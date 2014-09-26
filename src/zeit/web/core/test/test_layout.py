# -*- coding: utf-8 -*-


def test_macro_wrapper_handling_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    lines = tpl.module.wrapper_handling().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    script_tag = '<script type="text/javascript">'
    func_cookie = 'function getCookie'
    func_ressort = 'getRessort: function()'
    func_hide = 'hideZMOHeader: function( $nav )'
    func_margin = 'setHeaderMargin: function( _density_independant_pixels )'
    obj_wrapper = 'window.wrapper'
    assert script_tag in output, 'Script tag exists'
    assert func_cookie in output, 'getCookie function exists'
    assert func_ressort in output, 'getRessort function exists'
    assert func_hide in output, 'hideZMOHeader function exists'
    assert func_margin in output, 'setHeaderMargin function exists'
    assert obj_wrapper in output, 'wrapper object exists'
