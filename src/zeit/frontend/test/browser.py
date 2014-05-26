import cssselect
import lxml.html
import zope.testbrowser.browser


class Browser(zope.testbrowser.browser.Browser):
    """Custom testbrowser class that allows direct access to CSS selection on
    its content.

    Usage examples:

    # Create test browser
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

    _translator = None

    def __init__(self, *args, **kwargs):
        """Call base constructor and cache a translator instance."""
        super(Browser, self).__init__(*args, **kwargs)
        self._translator = cssselect.HTMLTranslator()

    def cssselect(self, selector):
        """Return a list of lxml.HTMLElement instances that match a given CSS
        selector."""
        xpath = self._translator.css_to_xpath(selector)
        if self.document is not None:
            return self.document.xpath(xpath)
        return None

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self.contents is not None:
            return lxml.html.document_fromstring(self.contents)
        return None
