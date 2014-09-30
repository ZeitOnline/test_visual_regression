# -*- coding: utf-8 -*-

import mock

def test_macro_wrapper_handling_produce_markup(jinja2_env):
    # ToDo: This needs refactoring.
    # We should not rely on string comparison, if we want to
    # test runnable code.
    tpl = jinja2_env.get_template(
        'zeit.web.core:templates/macros/layout_macro.tpl')
    obj = mock.Mock()
    lines = tpl.module.wrapper_handling(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    script_tag = '<script type="text/javascript">'
    func_cookie = 'function getCookie'
    func_ressort = 'getRessort: function()'
    func_hide = 'hideZMOHeader: function( $nav )'
    func_margin = 'setHeaderMargin: function( _density_independant_pixels )'
    obj_wrapper = 'window.wrapper'
    assert script_tag in output, 'Script tag doesnt exist'
    assert func_cookie in output, 'getCookie function doesnt exist'
    assert func_ressort in output, 'getRessort function doesnt exist'
    assert func_hide in output, 'hideZMOHeader function doesnt exist'
    assert func_margin in output, 'setHeaderMargin function doesnt exist'
    assert obj_wrapper in output, 'wrapper object doesnt exist'
