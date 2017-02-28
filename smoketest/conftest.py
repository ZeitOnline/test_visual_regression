import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pytest
import selenium.webdriver
import selenium.webdriver.firefox.firefox_binary


BROWSERS = {
    'firefox': selenium.webdriver.Firefox,
}


# XXX copy&paste from zeit.web.conftest, so we're independent of zeit.web and
# its dependencies.
@pytest.fixture(scope='session', params=BROWSERS.keys())
def selenium_driver(request):
    if request.param == 'firefox':
        parameters = {}
        profile = selenium.webdriver.FirefoxProfile(
            os.environ.get('ZEIT_WEB_FF_PROFILE'))
        profile.default_preferences.update({
            'network.http.use-cache': False,
            'browser.startup.page': 0,
            'browser.startup.homepage_override.mstone': 'ignore'})
        profile.update_preferences()
        parameters['firefox_profile'] = profile
        # Old versions: <https://ftp.mozilla.org/pub/firefox/releases/>
        ff_binary = os.environ.get('ZEIT_WEB_FF_BINARY')
        if ff_binary:
            parameters['firefox_binary'] = (
                selenium.webdriver.firefox.firefox_binary.FirefoxBinary(
                    ff_binary))
        browser = BROWSERS[request.param](**parameters)
    else:
        browser = BROWSERS[request.param]()
    request.addfinalizer(lambda *args: browser.quit())

    timeout = int(os.environ.get('ZEIT_WEB_FF_TIMEOUT', 30))
    original_get = browser.get

    def get_and_wait_for_body(self, *args, **kw):
        result = original_get(*args, **kw)
        WebDriverWait(self, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        return result
    browser.get = get_and_wait_for_body.__get__(browser)

    return browser
