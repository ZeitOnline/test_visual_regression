# -*- coding: utf-8 -*-


def test_article_page_should_contain_blocks(testserver, httpbrowser):
    browser = httpbrowser(
        '%s/zeit-magazin/article/all-blocks' % testserver.url)
    page = browser.cssselect('.article__page')[0]

    paragraph = browser.cssselect('.paragraph')
    intertitle = browser.cssselect('.article__subheading')
    contentadblock = browser.cssselect('#iq-artikelanker')
    portraitbox = page.cssselect('.portraitbox.figure-stamp')
    raw = page.cssselect('.raw')

    assert len(paragraph) == 9
    assert 'paragraph article__item' in paragraph[0].get('class')

    assert len(intertitle) == 5
    assert 'article__subheading article__item' in intertitle[0].get('class')

    assert len(portraitbox) == 1
    assert len(raw) == 1
    assert len(contentadblock) == 1

    # liveblog
    assert page.cssselect('.liveblog')


def test_article_should_render_variants_of_block_citation(testbrowser):
    browser = testbrowser('/zeit-magazin/article/all-blocks')
    citations = browser.cssselect('.quote')

    # short layout
    assert 'quote--short' in citations[0].get('class')

    # default layout
    assert 'quote--' not in citations[1].get('class')

    # wide layout
    assert 'quote--wide' in citations[2].get('class')


def test_article_contains_authorbox(testbrowser):
    browser = testbrowser('/zeit-online/article/authorbox')
    authorbox = browser.cssselect('.authorbox')
    assert len(authorbox) == 3

    author = authorbox[1]
    image = author.cssselect('[itemprop="image"]')[0]
    name = author.cssselect('strong[itemprop="name"]')[0]
    description = author.cssselect('[itemprop="description"]')[0]
    url = author.cssselect('a[itemprop="url"]')[0]

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.get('itemscope') is not None
    assert ('http://localhost/autoren/W/Jochen_Wegner/jochen-wegner/square'
            ) in image.cssselect('[itemprop="url"]')[0].get('content')
    assert name.text.strip() == 'Jochen Wegner'
    assert description.text.strip() == 'Chefredakteur, ZEIT ONLINE.'
    assert url.get('href') == 'http://localhost/autoren/W/Jochen_Wegner/index'
