import gocept.httpserverlayer.static
import os
import pytest
import time
import zeit.frontend.jinja


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

    loader = zeit.frontend.jinja.HTTPLoader(template_server.url)
    UNUSED_ENVIRONMENT = None
    source, path, uptodate = loader.get_source(UNUSED_ENVIRONMENT, 'foo.html')
    assert 'foo' == source


def touch(filename, time):
    os.utime(filename, (time, time))


def test_checks_uptodate_using_last_modified_header(template_server):
    template = template_server['documentroot'] + '/foo.html'
    open(template, 'w').write('foo')

    loader = zeit.frontend.jinja.HTTPLoader(template_server.url)
    UNUSED_ENVIRONMENT = None
    source, path, uptodate = loader.get_source(UNUSED_ENVIRONMENT, 'foo.html')

    assert uptodate()
    later = time.time() + 1
    touch(template, later)
    assert not uptodate()
