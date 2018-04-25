# -*- coding: utf-8 -*-
import datetime

import pytest

import zeit.cms.interfaces

import zeit.web.magazin.view_article


def test_longform_contains_subpage_index(testbrowser):
    browser = testbrowser('/zeit-magazin/article/05')
    index = browser.cssselect('.article__subpage-index')

    assert len(index) == 4

    for i, toc in enumerate(index):
        items = toc.cssselect('li')
        assert toc.cssselect('h3')
        assert toc.cssselect('ol')
        assert len(items) == 4
        for k, item in enumerate(items):
            if k == i:
                assert item.cssselect('.article__subpage-active')
            else:
                link = item.cssselect('a')[0]
                assert link.get('href') == '#kapitel{}'.format(k + 1)


def test_longform_contains_subpage_head(testbrowser):
    browser = testbrowser('/zeit-magazin/article/05')
    headlines = browser.cssselect('.article__subpage-head')
    assert len(headlines) == 4

    for i, headline in enumerate(headlines):
        assert headline.get('id') == 'kapitel{}'.format(i + 1)


def test_article_page_should_contain_blocks(httpbrowser):
    browser = httpbrowser('/zeit-magazin/article/all-blocks')
    page = browser.cssselect('.article-page')[0]

    paragraph = browser.cssselect('.paragraph')
    intertitle = browser.cssselect('.article__subheading')
    contentadblock = browser.cssselect('#iq-artikelanker')
    portraitbox = page.cssselect('.portraitbox')
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

    # test custom biography
    author = authorbox[0]
    description = author.cssselect('.authorbox__summary')[0]
    assert description.text.strip() == 'Text im Feld Kurzbio'
    assert description.get('itemprop') == 'description'

    # test author content and microdata
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


def test_article_header_contains_authors(testbrowser):
    browser = testbrowser('/zeit-magazin/article/08')
    authors = browser.cssselect('span[itemprop="author"]')
    link = authors[0].cssselect('a[itemprop="url"]')[0]
    assert len(authors) == 2
    assert authors[0].text_content() == 'Anne Mustermann, Berlin'
    assert authors[1].text_content() == 'Oliver Fritsch, London'
    assert link.get('href') == 'http://localhost/autoren/anne_mustermann'
    assert link.text_content() == 'Anne Mustermann'


def test_article_header_without_author(testbrowser):
    browser = testbrowser('zeit-magazin/article/martenstein-portraitformat')
    authors = browser.cssselect('span[itemprop="author"]')
    assert not authors


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'zeit-magazin/article/03',
        'zeit-magazin/article/03/seite-2',
        'zeit-magazin/article/03/komplettansicht',
        'zeit-magazin/article/standardkolumne-beispiel',
        'zeit-magazin/article/05',
        'feature/feature_longform'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


@pytest.mark.parametrize('last_published, first_released, contained', [
    (None, datetime.datetime(2014, 1, 1), False),
    (datetime.datetime(2014, 1, 2), datetime.datetime(2014, 1, 1), True)])
def test_seo_publish_date_script_should_be_generated_conditionally(
        last_published, first_released, contained, dummy_request, tplbrowser):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/03')
    view = zeit.web.magazin.view_article.Article(context, dummy_request)

    view.date_last_published_semantic = last_published
    view.date_first_released = first_released
    view.show_date_format_seo = 'short'

    browser = tplbrowser(
        'zeit.web.magazin:templates/content.html',
        view=view, request=dummy_request)

    inline_scritps = ''.join(browser.xpath('//script/text()'))
    assert ('1. Januar 2014' in inline_scritps) == contained


def test_volume_teaser_uses_zmo_printcover(testbrowser):
    browser = testbrowser('/zeit-magazin/article/volumeteaser')
    image = browser.cssselect('img.volume-teaser__media-item')
    assert len(image) == 1
    assert 'zeit-wissen' in image[0].get('src')


def test_article_shows_zplus_badge_for_paid_article(testbrowser):
    browser = testbrowser('/zeit-magazin/article/zplus-zmo-paid')
    badge = browser.cssselect('.zplus-badge')[0]
    text = badge.cssselect('.zplus-badge__text')[0]

    assert text.text.strip() == u'Exklusiv für Abonnenten'
    assert badge.cssselect('.zplus-badge__logo')


def test_article_shows_no_zplus_badge_for_metered_article(testbrowser):
    browser = testbrowser('/zeit-magazin/article/zplus-zmo-register')
    assert not browser.cssselect('.zplus-badge')


def test_zmo_advertorial_has_no_home_button_as_pagination(testbrowser):
    browser = testbrowser('/zeit-magazin/article/advertorial-onepage')
    assert len(browser.cssselect('.article-pagination__link')) == 0


def test_zmo_article_has_series_link(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    series_link = browser.cssselect('.meta__serie')
    assert len(series_link) == 1
    assert series_link[0].get('href').endswith('/serie/weinkolumne')


def test_canonical_url_should_contain_first_page_on_full_view(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03/komplettansicht')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('zeit-magazin/article/03')
