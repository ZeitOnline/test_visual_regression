# -*- coding: utf-8 -*-


def test_article_should_render_block_paragraph(testbrowser):
    browser = testbrowser('/zeit-magazin/article/article_all_blocks')
    paragraph = browser.cssselect('.article__body p')
    assert len(paragraph) == 7
    assert 'is-constrained is-centered' in paragraph[0].get('class')


def test_article_should_render_block_intertitle(testbrowser):
    browser = testbrowser('/zeit-magazin/article/article_all_blocks')
    intertitle = browser.cssselect('.article__body .article__subheading')
    assert len(intertitle) == 1
    assert 'article__subheading' in intertitle[0].get('class')


def test_article_should_render_block_citation(testbrowser):
    browser = testbrowser('/zeit-magazin/article/article_all_blocks')
    citations = browser.cssselect('.article__body blockquote')
    # short layout
    assert citations[0].get('class').strip().startswith('quote')
    # wide layout
    assert citations[1].get('class').strip().startswith('quote')\
        and citations[1].get('class').strip().endswith('--wide')
