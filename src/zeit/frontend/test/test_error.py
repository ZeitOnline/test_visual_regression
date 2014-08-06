# -*- coding: utf-8 -*-
import zeit.frontend.view_article
from zeit.frontend.test import Browser


def test_error_page_renders_on_internal_server_error(monkeypatch, testserver):

    def is_hp():
        def fget(self):
            raise Exception()
        return locals()

    monkeypatch.setattr(
        zeit.frontend.view_centerpage.Centerpage,
        'is_hp',
        property(**is_hp())
    )

    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert 'Internal Server Error' in browser.cssselect('h1')[0].text


def test_error_page_does_not_render_on_not_found_error(testserver):
    browser = Browser('%s/centerpage/lifestyle' % testserver.url)
    assert 'Dokument nicht gefunden' in browser.cssselect('h1')[0].text
