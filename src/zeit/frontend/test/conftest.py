from pytest_localserver.http import WSGIServer
from selenium import webdriver
from webtest import TestApp
from os.path import abspath, dirname, join, sep
import pytest
import zeit.frontend.application


def test_asset_path(*parts):
    """ Return full file-system path for given test asset path. """
    from zeit import frontend
    return abspath(join(dirname(frontend.__file__), 'data', *parts))


def test_asset(path):
    """ Return file-object for given test asset path. """
    return open(test_asset_path(*path.split(sep)), 'rb')


settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',
    'image_base_path': test_asset_path(),
}


browsers = {
    'firefox': webdriver.Firefox
    #'phantomjs': webdriver.PhantomJS,
}


@pytest.fixture(scope='session')
def application():
    return zeit.frontend.application.Application()({}, **settings)


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


@pytest.fixture
def asset():
    return test_asset


@pytest.fixture
def browser(application):
    """ Returns an instance of `webtest.TestApp`. """
    extra_environ = dict(HTTP_HOST='example.com')
    return TestApp(application, extra_environ=extra_environ)
