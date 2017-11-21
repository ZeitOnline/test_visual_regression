# -*- coding: utf-8 -*-
import urllib2

import zeit.cms.interfaces

import zeit.web.core.template


def test_link_object_should_redirect_permanently(testbrowser, monkeypatch):
    browser = testbrowser()
    browser.mech_browser.set_handle_redirect(False)
    try:
        browser.open('/blogs/nsu-blog-bouffier')
    except urllib2.HTTPError, e:
        assert (
            'http://blog.zeit.de/nsu-prozess-blog/2015/02/25'
            '/medienlog-zwickau-zschaepe-yozgat-verfassungsschutz-bouffier/' ==
            e.hdrs.get('location'))

    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'https': True}.get)

    try:
        browser.open('/blogs/nsu-blog-bouffier')
    except urllib2.HTTPError, e:
        assert (
            'https://blog.zeit.de/nsu-prozess-blog/2015/02/25'
            '/medienlog-zwickau-zschaepe-yozgat-verfassungsschutz-bouffier/' ==
            e.hdrs.get('location'))


def test_link_object_teaser_should_point_directly_to_destination(testbrowser):
    # test it for ZMO
    browser = testbrowser('/zeit-magazin/misc')
    href = ('http://www.zeit.de/zeit-magazin/mode-design/2014-05/'
            'karl-lagerfeld-interview')
    assert browser.cssselect('.teaser-fullwidth a[href="%s"]' % href)
    # test it for ZON
    browser = testbrowser('/zeit-online/link-object')
    href = ('http://blog.zeit.de/nsu-prozess-blog/2015/02/25/'
            'medienlog-zwickau-zschaepe-yozgat-verfassungsschutz-bouffier/')
    assert browser.cssselect('.teaser-fullwidth a[href="%s"]' % href)


def test_create_url_filter_should_create_correct_url(application):
    path = '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview'
    obj = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de%s-2' % path)
    assert zeit.web.core.template.create_url(None, obj) == (
        'http://www.zeit.de' + path)


def test_link_object_should_point_to_https_target_if_possible(application,
                                                              monkeypatch):
    monkeypatch.setattr(zeit.web.core.template, 'toggles', lambda x: True)
    link = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/'
        'mode-design/2014-05/karl-lagerfeld-interview-2')
    assert zeit.web.core.template.create_url(None, link) == (
        'https://www.zeit.de/zeit-magazin/mode-design/'
        '2014-05/karl-lagerfeld-interview')
