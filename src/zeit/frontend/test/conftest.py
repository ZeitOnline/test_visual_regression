from pytest_localserver.http import WSGIServer
from selenium import webdriver
import pytest
import zeit.frontend.application

settings = {
    'pyramid.reload_templates': 'false',
    'pyramid.debug_authorization': 'false',
    'pyramid.debug_notfound': 'false',
    'pyramid.debug_routematch': 'false',
    'pyramid.debug_templates': 'false',
}

browsers = {
    'firefox': webdriver.Firefox
    #'phantomjs': webdriver.PhantomJS,
}


@pytest.fixture(scope='session')
def application():
    return zeit.frontend.application.Application()(settings)


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
