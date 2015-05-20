# -*- coding: utf-8 -*-
import exceptions
import pytest
import requests

import zeit.web.core.view_centerpage
from zeit.web.magazin.view_centerpage import Centerpage
import zeit.web.core.template


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

message = '{} should not bother friedbert.'


def test_url_path_not_found_should_render_404(testserver):
    resp = requests.get('%s/centerpage/lifestyle' % testserver.url)
    assert u'Dokument nicht gefunden' in resp.text


def test_not_renderable_content_object_should_trigger_restart(testserver):
    resp = requests.get('%s/quiz-workaholic' % testserver.url)
    assert resp.headers['x-render-with'] == 'default'


def test_uncaught_exception_renders_500(monkeypatch, debug_testserver):
    def raise_exc(exc, *args):
        """Helper function for raising exceptions without using the builtin
        `raise` statement."""
        raise exc(*args)

    monkeypatch.setattr(Centerpage, 'title',
                        property(lambda self: raise_exc(Exception)))

    resp = requests.get('%s/centerpage/lebensart' % debug_testserver.url)
    assert u'Dokument zurzeit nicht verfügbar' in resp.text


@pytest.mark.parametrize('markup,assertion,kw', faulty_templates,
                         ids=[message.format(i[1]) for i in faulty_templates])
def test_failsafe_rendering(markup, assertion, kw):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string(markup)
    condition = isinstance(tpl.render(**kw), basestring)
    assert condition, message.format(assertion)
