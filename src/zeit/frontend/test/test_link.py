from zope.testbrowser.browser import Browser


def test_link_object_should_redirect_permanently(testserver):
    path = 'zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    browser = Browser('%s/%s-2' % (testserver.url, path))
    assert 'http://www.zeit.de/%s' % path == browser.url
