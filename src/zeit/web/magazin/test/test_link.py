# -*- coding: utf-8 -*-
import zeit.cms.interfaces

import zeit.web.core.template


def test_link_object_should_redirect_permanently(testserver, testbrowser):
    path = 'zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    browser = testbrowser('%s/%s-2' % (testserver.url, path))
    assert 'http://www.zeit.de/%s' % path == browser.url


def test_link_object_teaser_should_lead_directly_to_destination(
        testserver, testbrowser):
    url = '%s/zeit-magazin/test-cp/test-cp-zmo-3' % testserver.url
    assert ('<a href="http://www.zeit.de/zeit-magazin/mode-design/2014-05/'
            'karl-lagerfeld-interview">') in testbrowser(url).contents


def test_create_url_filter_should_create_correct_url(testserver, testbrowser):
    path = '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    obj = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de%s-2' % path)
    assert zeit.web.core.template.create_url(None, obj) == (
        'http://www.zeit.de' + path)
