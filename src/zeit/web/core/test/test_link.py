# -*- coding: utf-8 -*-
import zeit.cms.interfaces

import zeit.web.core.template


def test_link_object_should_redirect_permanently(testbrowser):
    browser = testbrowser('blogs/nsu-blog-bouffier')
    assert (
        'http://blog.zeit.de/nsu-prozess-blog/2015/02/25'
        '/medienlog-zwickau-zschaepe-yozgat-verfassungsschutz-bouffier/' ==
        browser.url)


def test_link_object_teaser_should_lead_directly_to_destination(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-3')
    assert ('<a href="http://www.zeit.de/zeit-magazin/mode-design/2014-05/'
            'karl-lagerfeld-interview">') in browser.contents


def test_create_url_filter_should_create_correct_url(testserver, testbrowser):
    path = '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    obj = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de%s-2' % path)
    assert zeit.web.core.template.create_url(None, obj) == (
        'http://www.zeit.de' + path)
