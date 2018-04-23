import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import cssselect
import json
import lxml.html
import pytest
import requests
import selenium.webdriver
import selenium.webdriver.firefox.firefox_binary


TESTCONFIG_STAGING = {
    'ENV': 'STAGING',
    'BASE_URL': 'http://www.staging.zeit.de',
    'TIMEOUT': 20,
    'NEWSFEED_BASE_URL': 'http://newsfeed.staging.zeit.de',
    'MEMBER_BASE_URL': 'https://meine.staging.zeit.de',
    'MEMBER_USERNAME': 'thomas.strothjohann+unmoderiert1@apps.zeit.de',
    'MEMBER_PASSWORD': 'unmoderierteins'
}

TESTCONFIG_PRODUCTION = {
    'ENV': 'PRODUCTION',
    'BASE_URL': 'https://www.zeit.de',
    'TIMEOUT': 10,
    'NEWSFEED_BASE_URL': 'https://newsfeed.zeit.de',
    'MEMBER_BASE_URL': 'https://meine.zeit.de',
    'MEMBER_USERNAME': 'leser-moderiert@example.com',
    'MEMBER_PASSWORD': 'pytestEnd2End'
}


@pytest.fixture(scope='session')
def config():
    environment = os.environ.get('ZEIT_WEB_SMOKETESTS', 'STAGING')
    return globals()['TESTCONFIG_%s' % environment]


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
            ec.presence_of_element_located((By.TAG_NAME, "body")))
        return result
    browser.get = get_and_wait_for_body.__get__(browser)

    return browser


@pytest.fixture
def testbrowser():
    return BaseBrowser()


# When testing ESI fragments, autodetection of the encoding may not work (no
# head, so no meta charset declaration), so we specify it explicitly.
HTML_PARSER = lxml.html.HTMLParser(encoding='UTF-8')


class BaseBrowser(object):
    """Base class for custom test browsers that allow direct access to CSS and
    XPath selection on their content.

    Usage examples:

    # Create a test browser
    browser = Browser('/foo/bar')
    # Test only one h1 exists
    assert len(browser.cssselect('h1.only-once')) == 1
    # Test all divs contain at least one span
    divs = browser.cssselect('div')
    assert all(map(lambda d: d.cssselect('span'), divs))
    # Test the third paragraph has two links with class batz
    paragraph = browser.cssselect('p')[2]
    assert len(paragraph.cssselect('a.batz')) == 2

    """

    def __call__(self, uri=None, **kw):
        if uri is not None:
            self.open(uri, **kw)
        return self

    def open(self, uri, **kw):
        r = requests.get(uri, **kw)
        self.contents = r.text

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self.contents is not None:
            return lxml.html.document_fromstring(
                self.contents, parser=HTML_PARSER)

    @property
    def json(self):
        """Return a dictionary of the parsed json body if available."""
        if self.contents is not None:
            return json.loads(self.contents)

    def cssselect(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given CSS
        selector.
        """
        xpath = cssselect.HTMLTranslator().css_to_xpath(selector)
        if self.document is not None:
            return self.document.xpath(xpath)

    def xpath(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given
        XPath selector.
        """
        if self.document is not None:
            return self.document.xpath(selector)
