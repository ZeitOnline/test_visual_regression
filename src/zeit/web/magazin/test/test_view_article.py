# -*- coding: utf-8 -*-
import lxml


def test_article_page_should_contain_blocks(testbrowser):
    browser = testbrowser('/zeit-magazin/article/all-blocks')
    page = browser.cssselect('.article__page')
    html_str = lxml.html.tostring(page[0])

    paragraph = browser.cssselect('.paragraph')
    intertitle = browser.cssselect('.article__subheading')
    contentadblock = browser.cssselect('#iq-artikelanker')
    portraitbox = page[0].cssselect('.portraitbox.figure-stamp')
    raw = page[0].cssselect('.raw')

    assert len(paragraph) == 11
    assert 'paragraph article__item' in paragraph[0].get('class')

    assert len(intertitle) == 7
    assert 'article__subheading article__item' in intertitle[0].get('class')

    assert len(portraitbox) == 1
    assert len(raw) == 1
    assert len(contentadblock) == 1

    # liveblog
    assert '<include src="http://www.zeit.de/liveblog-backend/100.html"' \
           ' onerror="continue"></include>' in html_str


def test_article_should_render_variants_of_block_citation(testbrowser):
    browser = testbrowser('/zeit-magazin/article/all-blocks')
    citations = browser.cssselect('.quote')

    # short layout
    assert 'quote--short' in citations[0].get('class')

    # default layout
    assert 'quote--' not in citations[1].get('class')

    # wide layout
    assert 'quote--wide' in citations[2].get('class')
