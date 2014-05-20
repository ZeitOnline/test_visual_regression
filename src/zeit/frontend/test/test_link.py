from zope.testbrowser.browser import Browser
import zeit.cms.interfaces


def test_link_object_should_redirect_permanently(testserver):
    path = 'zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    browser = Browser('%s/%s-2' % (testserver.url, path))
    assert 'http://www.zeit.de/%s' % path == browser.url


def test_link_object_teaser_should_lead_directly_to_destination(testserver):
    url = '%s/zeit-magazin/test-cp/test-cp-zmo-3' % testserver.url
    assert ('<a href="http://www.zeit.de/zeit-magazin/mode-design/2014-05/'
            'karl-lagerfeld-interview">') in Browser(url).contents


def test_create_url_filter_should_create_correct_url(testserver):
    path = '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    obj = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de%s-2' % path)
    from zeit.frontend.application import create_url
    assert create_url(None, obj) == 'http://www.zeit.de' + path
