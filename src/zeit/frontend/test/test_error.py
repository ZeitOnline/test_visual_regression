# -*- coding: utf-8 -*-

import pytest
import jinja2.environment
import jinja2.runtime

import zeit.frontend.template
import zeit.frontend.view_article
from zeit.frontend.test import Browser


def test_error_page_renders_on_internal_server_error(monkeypatch, testserver):

    def fget(self):
        raise Exception

    monkeypatch.setattr(
        zeit.frontend.view_centerpage.Centerpage,
        'is_hp',
        property(fget=fget)
    )

    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert 'Internal Server Error' in browser.cssselect('h1')[0].text


def test_error_page_does_not_render_on_not_found_error(testserver):
    browser = Browser('%s/centerpage/lifestyle' % testserver.url)
    assert 'Dokument nicht gefunden' in browser.cssselect('h1')[0].text


class BadClass(object):
    @property
    def attr_err(self):
        raise AttributeError

    @property
    def exception(self):
        raise Exception

self = jinja2.runtime.TemplateReference(
    jinja2.environment.Template('')
)


@pytest.mark.parametrize('markup,assertion,kw', [
    ('{% bad %}',
     'Unknown tags',
     {}),
    ('{% if %}',
     'Incomplete control statements',
     {}),
    ('{% for bad in [] %} foo {% endif %}',
     'Inconsistent tag structure',
     {}),
    ('{% - if bad %} foo {% endif + %}',
     'Misuse of whitespace control',
     {}),
    ('{% block good %} foo {% endblock bad %}',
     'Miscaptioned end-tags',
     {}),
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
    ('{{ good.attr_err }}',
     'AttributeErrors hidden in a property',
     {'good': BadClass()}),
    ('{{ good.exception }}',
     'Raising generic Exceptions in a property',
     {'good': BadClass()}),
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
    ('{{ bad|bad }}',
     'Applying unknown filters to unknown variables',
     {}),
    ('{{ good|bad }}',
     'Applying unknown filters to known objects',
     {'good': object()}),
    ('{{ good|bad|bad }}',
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
     {'self': self}),
    ('{{ lipsum(bad=True) }}',
     'Calling builtin function with wrong signature',
     {}),
    ('{{ 100 / 0 }}',
     'Insanity',
     {})
])
def test_failsafe_rendering(markup, assertion, kw):
    env = zeit.frontend.template.Environment()
    tpl = env.from_string(markup)
    condition = isinstance(tpl.render(**kw), basestring)
    assert condition, assertion + ' should not bother friedbert.'
