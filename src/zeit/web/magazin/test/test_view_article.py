# -*- coding: utf-8 -*-
import lxml


def test_article_page_should_contain_blocks(testbrowser):
    browser = testbrowser('/zeit-magazin/article/article_all_blocks')
    page = browser.cssselect('.article__page')
    html_str = lxml.html.tostring(page[0])

    paragraph = browser.cssselect('.article__body p')
    intertitle = browser.cssselect('.article__body .article__subheading')
    contentadblock = browser.cssselect('#iq-artikelanker')
    portraitbox = page[0].cssselect('.portraitbox.figure-stamp')
    raw = page[0].cssselect('.raw')

    assert len(paragraph) == 7
    assert 'paragraph article__item' in paragraph[0].get('class')

    assert len(intertitle) == 1
    assert 'article__subheading' in intertitle[0].get('class')

    assert len(portraitbox) == 1
    assert len(raw) == 1
    assert len(contentadblock) == 1

    # liveblog
    assert '<include src="http://www.zeit.de/liveblog-backend/100.html"' \
           ' onerror="continue"></include>' in html_str


def test_article_should_render_variants_of_block_citation(testbrowser):
    browser = testbrowser('/zeit-magazin/article/article_all_blocks')
    citations = browser.cssselect('.article__body blockquote')

    # short layout
    assert citations[0].get('class').strip().startswith('quote')

    # wide layout
    assert citations[1].get('class').strip().startswith('quote')\
        and citations[1].get('class').strip().endswith('--wide')
