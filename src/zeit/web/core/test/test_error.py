# -*- coding: utf-8 -*-
import exceptions
import sys

import pytest
import requests
import venusian

import zeit.web.magazin.view_centerpage
import zeit.web.core.decorator
import zeit.web.core.template
import zeit.web.core.view_centerpage


class Raiser(object):
    """Testing purpose class for raising any of Python's builtin exceptions.
    Properties with a camel-cased variant of the exception's name raise the
    corresponding Exception on access.
    Usage examples:

        Raiser().key_error
        Raiser().system_exit
    """
    def __getattr__(self, name):
        cls = ''.join(x.capitalize() or '_' for x in name.split('_'))
        if not hasattr(exceptions, cls):
            return super(Raiser, self).__getattr__(name)
        raise getattr(exceptions, cls)()


faulty_templates = [
    ('{{ bad }}',
     'Unknown variables',
     {}),
    ('{{ bad() }}',
     'Unknown callables',
     {}),
    ('{{ bad[0] }}',
     'Indexing an unknown variable',
     {}),
    ('{{ bad.bad }}',
     'Accessing an attribute of an unknown variable',
     {}),
    ('{{ good.bad }}',
     'Accessing an unknown attribute of an object',
     {'good': object()}),
    ('{{ good.attribute_error }}',
     'AttributeErors hidden in a property',
     {'good': Raiser()}),
    ('{{ good.standard_error }}',
     'Raising generic Exceptions in a property',
     {'good': Raiser()}),
    ('{{ good.bad() }}',
     'Calling an unknown method of an object',
     {'good': object()}),
    ('{{ good.bad[0] }}',
     'Indexing an unknown attribute of an object',
     {'good': object()}),
    ('{{ good.bad.bad }}',
     'Accessing an attribute of an unknown attribute',
     {'good': object()}),
    ('{% if good.bad %} foo {% endif %}',
     'Conditionals on unknown attributes',
     {'good': object()}),
    ('{% if good.bad() %} foo {% endif %}',
     'Conditionals on unknown methods',
     {'good': object()}),
    ('{% if good.bad[0] %} foo {% endif %}',
     'Conditionals on unindexable attributes',
     {'good': object()}),
    ('{% if good.bad.bad %} foo {% endif %}',
     'Conditionals on attributes of unknown attributes',
     {'good': object()}),
    ('{% for item in bad %} foo {% endfor %}',
     'Looping over unknown variables',
     {}),
    ('{% for item in bad() %} foo {% endfor %}',
     'Looping over unknown callables',
     {}),
    ('{% for item in bad[0] %} foo {% endfor %}',
     'Looping over unindexable variables',
     {}),
    ('{% for item in bad.bad %} foo {% endfor %}',
     'Looping over attributes of unknown variables',
     {}),
    ('{{ bad | bad }}',
     'Applying unknown filters to unknown variables',
     {}),
    ('{{ good | bad }}',
     'Applying unknown filters to known objects',
     {'good': object()}),
    ('{{ good | bad | bad }}',
     'Chaining unknown filters',
     {'good': object()}),
    ('{% if good is bad %} foo {% endif %}',
     'Testing objects against unknown tests',
     {'good': object()}),
    ('{% if bad is iterable %} foo {% endif %}',
     'Testing unknown variables against builtin test',
     {}),
    ('{% if bad is bad %} foo {% endif %}',
     'Testing unknown variables against unknown tests',
     {}),
    ('{% extends "bad.html" %}',
     'Extending a missing template',
     {}),
    ('{% include "bad.html" %}',
     'Including a missing template',
     {}),
    ('{% import "bad.html" as bad %}',
     'Importing a missing template',
     {}),
    ('{% set foo = good.bad %}',
     'Setting a local scope variable to an unknown attribute',
     {}),
    ('{{ self.bad() }}',
     'Referencing unknown parent template',
     {}),
    ('{{ lipsum(bad=True) }}',
     'Calling builtin function with wrong signature',
     {}),
    ('{{ 100 / 0 }}',
     'Insanity',
     {})]

message = '{} should not bother friedbert'


@pytest.mark.parametrize('markup,assertion,kw', faulty_templates,
                         ids=[message.format(i[1]) for i in faulty_templates])
def test_failsafe_rendering(markup, assertion, kw):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string(markup)
    condition = isinstance(tpl.render(**kw), basestring)
    assert condition, message.format(assertion)


def test_url_path_not_found_should_render_404(testserver):
    resp = requests.get('%s/zeit-magazin/centerpage/lifestyle'
                        % testserver.url)
    assert u'Dokument nicht gefunden' in resp.text


def test_not_renderable_content_object_should_trigger_restart(testserver):
    resp = requests.get('%s/zeit-online/quiz/quiz-workaholic' % testserver.url)
    assert resp.headers['x-render-with'] == 'default'


@zeit.web.core.decorator.JinjaEnvRegistrator('filters', category='_c1')
def do_things(arg, kw1=42, kw2=45):
    """Docstrings document things."""
    return arg * (kw2 - kw1)


def test_safeguarded_jinja_modifier_should_preserve_func(debug_application):
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c1',))
    tpl = env.from_string(u'{{ "foo" | do_things }}')
    assert tpl.render().strip() == 'foofoofoo'

    assert do_things.func_defaults == (42, 45)
    assert do_things.func_name == 'do_things'
    assert do_things.__doc__ == 'Docstrings document things.'
    assert do_things('bar', kw2=4, kw1=2) == 'barbar'


@zeit.web.core.decorator.JinjaEnvRegistrator('filters', category='_c2')
def faulty_filter(*args):
    1 / 0


def test_faulty_jinja_filter_should_not_bother_friedbert(debug_application):
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c2',))
    tpl = env.from_string(u'foo {{ 42 | bad }}')
    assert tpl.render().strip() == 'foo'


@zeit.web.core.decorator.JinjaEnvRegistrator('globals', category='_c3')
def faulty_global(*args):
    1 / 0


def test_faulty_jinja_global_should_not_bother_friedbert(debug_application):
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c3',))
    tpl = env.from_string(u'foo {{ bad(42) }}')
    assert tpl.render().strip() == 'foo'


@zeit.web.core.decorator.JinjaEnvRegistrator('tests', category='_c4')
def faulty_test(*args):
    1 / 0


def test_faulty_jinja_test_should_not_bother_friedbert(debug_application):
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c4',))
    tpl = env.from_string(u'foo {{ 42 is bad }}')
    assert tpl.render().strip() == 'foo'
