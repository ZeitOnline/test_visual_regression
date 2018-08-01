# -*- coding: utf-8 -*-
from StringIO import StringIO
import exceptions
import logging
import sys

import plone.testing.zca
import pytest
import venusian
import zope.browserpage.metaconfigure

import zeit.cms.testcontenttype.testcontenttype

import zeit.web.core.application
import zeit.web.core.decorator
import zeit.web.core.jinja


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


undefined_templates = [
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
    ('{% if good.bad %}{% endif %}',
     'Conditionals on unknown attributes',
     {'good': object()}),
    ('{% if good.bad() %}{% endif %}',
     'Conditionals on unknown methods',
     {'good': object()}),
    ('{% if good.bad[0] %}{% endif %}',
     'Conditionals on unindexable attributes',
     {'good': object()}),
    ('{% if good.bad.bad %}{% endif %}',
     'Conditionals on attributes of unknown attributes',
     {'good': object()}),
    ('{% for item in bad %}{% endfor %}',
     'Looping over unknown variables',
     {}),
    ('{% for item in bad() %}{% endfor %}',
     'Looping over unknown callables',
     {}),
    ('{% for item in bad[0] %}{% endfor %}',
     'Looping over unindexable variables',
     {}),
    ('{% for item in bad.bad %}{% endfor %}',
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
    ('{% if good is bad %}{% endif %}',
     'Testing objects against unknown tests',
     {'good': object()}),
    ('{% if bad is iterable %}{% endif %}',
     'Testing unknown variables against builtin test',
     {}),
    ('{% if bad is bad %}{% endif %}',
     'Testing unknown variables against unknown tests',
     {}),
    ('{% set foo = good.bad %}',
     'Setting a local scope variable to an unknown attribute',
     {}),
    ('{{ self.bad() }}',
     'Referencing unknown parent template',
     {})]

message = '{} should still render'


@pytest.mark.parametrize(
    'markup,assertion,kw', undefined_templates,
    ids=[message.format(i[1]) for i in undefined_templates])
def test_failsafe_rendering(markup, assertion, kw):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string('__result__' + markup)
    result = tpl.render(**kw)
    assert result == '__result__', message.format(assertion)


faulty_templates = [
    ('{% extends "bad.html" %}',
     'Extending a missing template',
     {}),
    ('{% include "bad.html" %}',
     'Including a missing template',
     {}),
    ('{% import "bad.html" as bad %}',
     'Importing a missing template',
     {}),
    ('{{ lipsum(bad=True) }}',
     'Calling builtin function with wrong signature',
     {}),
    ('{{ 100 / 0 }}',
     'Insanity',
     {})]

message = '{} should not bother friedbert'


@pytest.mark.parametrize(
    'markup,assertion,kw', faulty_templates,
    ids=[message.format(i[1]) for i in faulty_templates])
def test_exception_prevention(markup, assertion, kw):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string('__result__' + markup)
    result = tpl.render(**kw)
    assert result == '', message.format(assertion)


@zeit.web.core.decorator.JinjaEnvRegistrator('filters', category='_c1')
def do_things(arg, kw1=42, kw2=45):
    """Docstrings document things."""
    return arg * (kw2 - kw1)


def test_safeguarded_jinja_modifier_should_preserve_func():
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


def test_faulty_jinja_filter_should_not_bother_friedbert():
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c2',))
    tpl = env.from_string(u'foo {{ 42 | bad }}')
    assert tpl.render().strip() == 'foo'


def test_exception_in_builtin_filter_should_not_bother_friedbert():
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c2',))
    tpl = env.from_string(u'foo {{ "%02d" | format(None) }}')
    assert tpl.render().strip() == 'foo'


@zeit.web.core.decorator.JinjaEnvRegistrator('globals', category='_c3')
def faulty_global(*args):
    1 / 0


def test_faulty_jinja_global_should_not_bother_friedbert():
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c3',))
    tpl = env.from_string(u'foo {{ bad(42) }}')
    assert tpl.render().strip() == 'foo'


@zeit.web.core.decorator.JinjaEnvRegistrator('tests', category='_c4')
def faulty_test(*args):
    1 / 0


def test_faulty_jinja_test_should_not_bother_friedbert():
    env = zeit.web.core.jinja.Environment()
    venusian.Scanner(env=env).scan(sys.modules[__name__], categories=('_c4',))
    tpl = env.from_string(u'foo {{ 42 is bad }}')
    assert tpl.render().strip() == 'foo'


@pytest.fixture
def jinja_log(request):
    log = StringIO()
    handler = logging.StreamHandler(log)
    logger = logging.getLogger('zeit.web.core.jinja')
    logger.addHandler(handler)
    oldlevel = logger.level
    logger.setLevel(logging.DEBUG)

    def teardown():
        logger.removeHandler(handler)
        logger.setLevel(oldlevel)
    request.addfinalizer(teardown)
    return log


def test_undefined_error_logs_request_url(jinja_log):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string(u'{{ foo.bar }}')
    tpl.render()
    assert 'Undefined while rendering <unknown>' in jinja_log.getvalue()


def test_undefined_error_logs_classname_for_most_objects(jinja_log):
    env = zeit.web.core.jinja.Environment()
    tpl = env.from_string(u'{{ context.foo.bar }}')
    tpl.render(context={})
    assert "'dict object' has no attribute 'foo'" in jinja_log.getvalue()


def test_undefined_error_logs_repr_for_cms_content(jinja_log):
    env = zeit.web.core.jinja.Environment()
    content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
    content.uniqueId = u'http://xml.zeit.de/täst'
    tpl = env.from_string(u'{{ context.foo.bar }}')
    tpl.render(context=content)
    assert (
        "ExampleContentType http://xml.zeit.de/t\\\\xe4st>' has no "
        "attribute 'foo'" in jinja_log.getvalue())


# XXX Is there an easier/faster way to set up an Application with different
# settings than copying the application_session fixture wholesale?
@pytest.fixture
def error_swallowing_application(app_settings, request):
    plone.testing.zca.pushGlobalRegistry()
    zope.browserpage.metaconfigure.clear()
    request.addfinalizer(plone.testing.zca.popGlobalRegistry)
    app_settings = app_settings.copy()
    app_settings['jinja2.environment'] = 'zeit.web.core.jinja.Environment'
    factory = zeit.web.core.application.Application()
    app = factory({}, **app_settings)
    app.zeit_app = factory
    return app


def test_integration_jinja_environment_is_configured_for_ignoring_errors(
        error_swallowing_application):
    env = error_swallowing_application.zeit_app.jinja_env
    tpl = env.from_string(u'foo {{ 42 | bad }}')
    assert tpl.render().strip() == 'foo'
