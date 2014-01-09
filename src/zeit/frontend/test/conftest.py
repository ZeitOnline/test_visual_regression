from pyramid.testing import setUp, tearDown, DummyRequest
from pytest_localserver.http import WSGIServer
from selenium import webdriver
from os import path
import pytest
from webtest import TestApp as TestAppBase
import zeit.frontend.application
from zeit import frontend

settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',
    'agatho_url': u'file://%s/' % path.join(path.dirname(path.abspath(frontend.__file__)), 'data', 'comments')
}

browsers = {
    'firefox': webdriver.Firefox
    #'phantomjs': webdriver.PhantomJS,
}



@pytest.fixture(scope='session')
def application():
    return zeit.frontend.application.Application()(settings)


@pytest.fixture
def config(request):
    config = setUp(settings=settings)
    request.addfinalizer(tearDown)
    return config


@pytest.fixture
def dummy_request(request, config):
    config.manager.get()['request'] = req = DummyRequest(is_xhr=False)
    return req


@pytest.fixture
def agatho():
    from zeit.frontend.comments import Agatho
    return Agatho(agatho_url=settings['agatho_url'])


@pytest.fixture(scope='session')
def testserver(application, request):
    server = WSGIServer(application=application, port="6543")
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(scope='session', params=browsers.keys())
def selenium_driver(request):
    if request.param == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.http.use-cache', False)
        b = browsers[request.param](firefox_profile=profile)
    else:
        b = browsers[request.param]()

    request.addfinalizer(lambda *args: b.quit())
    return b


class TestApp(TestAppBase):

    def get_json(self, url, params=None, headers=None, *args, **kw):
        if headers is None:
            headers = {}
        headers['Accept'] = 'application/json'
        return self.get(url, params, headers, *args, **kw)



@pytest.fixture
def browser(application):
    """ Returns an instance of `webtest.TestApp`. """
    return TestApp(application, extra_environ=dict(HTTP_HOST='example.com'))
