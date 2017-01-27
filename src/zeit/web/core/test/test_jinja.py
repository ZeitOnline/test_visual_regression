import os
import sys
import time

import gocept.httpserverlayer.static
import jinja2
import lxml.html
import mock
import pytest
import venusian
import zope.component

import zeit.web.core.jinja


@pytest.fixture(scope='session')
def template_server_session(request):
    server = gocept.httpserverlayer.static.Layer(module=__name__)
    server.setUp()
    request.addfinalizer(server.tearDown)
    server.url = 'http://%s' % server['http_address']
    return server


@pytest.fixture
def template_server(template_server_session):
    template_server_session.testSetUp()
    return template_server_session


def test_retrieves_template_via_http(template_server):
    open(template_server['documentroot'] + '/foo.html', 'w').write('foo')

    loader = zeit.web.core.jinja.HTTPLoader(template_server.url)
    source, path, uptodate = loader.get_source(None, 'foo.html')
    assert 'foo' == source


def test_checks_uptodate_using_last_modified_header(template_server):
    template = template_server['documentroot'] + '/foo.html'
    open(template, 'w').write('foo')

    loader = zeit.web.core.jinja.HTTPLoader(template_server.url)
    source, path, uptodate = loader.get_source(None, 'foo.html')

    assert uptodate()
    later = time.time() + 1
    os.utime(template, (later, later))
    assert not uptodate()


def test_no_url_configured_yields_error_message():
    loader = zeit.web.core.jinja.HTTPLoader(url=None)
    source, path, uptodate = loader.get_source(None, 'foo.html')
    assert 'load_template_from_dav_url' in source


def test_jinja_env_registrator_registers_only_after_scanning(testserver):
    jinja = mock.Mock()
    jinja.foo = {}

    register_foo = zeit.web.core.decorator.JinjaEnvRegistrator('foo')
    do_foo = register_foo(lambda: 42)
    globals()['do_foo'] = do_foo

    assert do_foo() == 42
    assert jinja.foo == {}

    scanner = venusian.Scanner(env=jinja)
    scanner.scan(sys.modules[__name__], categories=('jinja',),)

    assert do_foo() == 42
    assert 'do_foo' in jinja.foo


def test_visual_profiler_should_not_interfere_with_rendering_if_disabled(
        testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert not len(browser.cssselect('div.__pro__'))

    browser = testbrowser('/zeit-magazin/index')
    assert not len(browser.cssselect('div.__pro__'))


def test_visual_profiler_should_inject_performance_visualization(application):
    # XXX I couldn't defeat isolation issues to do a full integration test
    #     with the profiler extension :pensive:
    #     So this is a very basic (but isolated) test setup. (ND)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['jinja2.enable_profiler'] = 'True'

    def world():
        return __import__('time').sleep(0.1) or 'world'

    env = jinja2.Environment()
    env.add_extension(zeit.web.core.jinja.ProfilerExtension)
    tpl = env.from_string(
        '{% profile %}Hello {{ world() }}{% endprofile%}',
        {'world': world})

    document = lxml.html.fromstring(tpl.render())

    assert len(document.cssselect('div.__pro__')) == 1
    assert document.cssselect('div.__pro__')[0].text == 'Hello world'
    assert int(document.cssselect('div.__pro__ b')[0].text.rstrip('ms'))


@pytest.mark.parametrize('expr, value', [('True', 'bar'), ('False', '')])
def test_require_extension_should_only_execute_if_expr_evaluates_to_true(
        jinja2_env, expr, value):
    tpl = '{% require foo = ' + expr + ' %} bar {% endrequire %}'
    assert jinja2_env.from_string(tpl).render().strip() == value


def test_require_extension_should_ensure_variable_access_in_inner_block(
        jinja2_env):
    tpl = '{% require foo = "pre" + fix %} {{ foo }} {% endrequire %}'
    assert jinja2_env.from_string(tpl).render(fix='fix').strip() == 'prefix'
