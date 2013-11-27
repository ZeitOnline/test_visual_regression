import pytest
from selenium import webdriver
from pytest_localserver.http import WSGIServer
from zeit.frontend.application import factory

settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',
}

browsers = {
    'firefox': webdriver.Firefox,
    'phantomjs': webdriver.PhantomJS,
}


@pytest.fixture(scope='session')
def testserver(request):
    server = WSGIServer(application=factory(settings), port="6543")
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
