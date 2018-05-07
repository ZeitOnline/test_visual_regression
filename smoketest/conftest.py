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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC  # NOQA


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


def pytest_addoption(parser):
    parser.addoption("--visible", action="store_true",
                     default=False, help="Show browser when running tests")


@pytest.fixture(scope='session')
def config():
    environment = os.environ.get('ZEIT_WEB_SMOKETESTS', 'STAGING')
    return globals()['TESTCONFIG_%s' % environment]

# 'chrome': selenium.webdriver.Chrome
# needs Chromedriver, install via brew install chromedriver
# or from https://sites.google.com/a/chromium.org/chromedriver/downloads
# Also needs Chrome or Chromium, if you use chromium,
# set path to Chromium in envorinment variable `ZEIT_WEB_CHROMIUM_BINARY`
BROWSERS = {
     'chrome': selenium.webdriver.Chrome,
}


def pytest_collection_modifyitems(items):
    """Mark all selenium tests by use of fixture selenium_driver
    to run only selenium test by invoking pytest -m selenium"""
    for item in items:
        try:
            fixtures = item.fixturenames
            if 'selenium_driver' in fixtures:
                item.add_marker(pytest.mark.selenium)
        except:
            pass


# XXX copy&paste from zeit.web.conftest, so we're independent of zeit.web and
# its dependencies.
@pytest.fixture(scope='session', params=BROWSERS.keys())
def selenium_driver(request):
    parameters = {}
    if request.param == 'chrome':
        opts = Options()
        if not request.config.getoption('--visible'):
            opts.add_argument('headless')
        opts.add_argument('disable-gpu')
        opts.add_argument('window-size=1200x800')
        chromium_binary = os.environ.get('ZEIT_WEB_CHROMIUM_BINARY')
        if chromium_binary:
            opts.binary_location = chromium_binary
        parameters['chrome_options'] = opts
    browser = BROWSERS[request.param](**parameters)
    request.addfinalizer(lambda *args: browser.quit())
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
