# -*- coding: utf-8 -*-
import mock

import zeit.cms.interfaces

import zeit.web.core.interfaces


def test_image_template_should_produce_figure_markup(
        tplbrowser, dummy_request):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl',
        block=image, request=dummy_request)
    assert browser.cssselect('figure.figure-full-width')
    assert browser.cssselect('img.figure__media')
    assert browser.cssselect('span.figure__copyright')
    assert browser.cssselect('a')[0].get('href') == 'http://links.to'


def test_image_template_should_produce_copyright_caption(
        tplbrowser, dummy_request):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl',
        block=image, request=dummy_request)
    copyright = browser.cssselect('.figure__copyright a')[0]
    assert copyright.get('href') == 'http://foo.com'
    assert copyright.text_content() == u'© Andreas Gebert/dpa'


def test_image_template_should_designate_correct_layouts(testbrowser):
    browser = testbrowser('/zeit-magazin/article/inline-imagegroup')
    header = browser.cssselect('.header-article__media-item')[0]
    assert header.get('data-ratio') == '1.77858439201'  # variant=original
    stamp = browser.cssselect('figure.figure-stamp--right img')[0]
    assert stamp.get('data-ratio') == '0.75'  # variant=portrait
    fullwidth = browser.cssselect('figure.is-centered img')[0]
    assert fullwidth.get('data-ratio') == '1.77777777778'  # variant=wide


def test_image_template_should_hide_none(testbrowser):
    # XXX I'd much rather change a caption in the article, but trying
    # to checkout raises ConstrainedNotSatisfiedError: xl-header. :-(
    with mock.patch('zeit.web.core.block._inline_html') as inline:
        inline.return_value = ''
        browser = testbrowser('/feature/feature_longform')
        assert '<span class="figure__text">None</span>' not in browser.contents
