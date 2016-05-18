# -*- coding: utf-8 -*-

import zeit.cms.interfaces

import zeit.web.campus.view_article


def test_article_should_render_full_view(testbrowser):
    browser = testbrowser('/campus/article/paginated/komplettansicht')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/paginated')
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_article_pagination_on_single_page(testbrowser):
    select = testbrowser('/campus/article/simple').cssselect

    assert len(select('.article-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 0
    # assert len(select('.article-toc')) == 0
    button = select('.article-pagination__button')[0]
    link = select('.article-pagination__link')[0].attrib['href']
    assert button.text.strip() == 'Mehr ZEIT Campus'
    assert 'campus/index' in link


def test_article_pagination_on_second_page(testbrowser):
    select = testbrowser('/campus/article/paginated/seite-2').cssselect

    assert len(select('.article-header')) == 0
    assert len(select('.page-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 1
    assert len(select('.article-pager')) == 1
    # assert len(select('.article-toc')) == 1
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == u'Nächste Seite'


def test_article_pagination_on_last_paginated_page(testbrowser):
    select = testbrowser('/campus/article/paginated/seite-10').cssselect

    assert len(select('.article-header')) == 0
    assert len(select('.page-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 1
    # assert len(select('.article-toc')) == 1
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == 'Mehr ZEIT Campus'


def test_article_pagination_on_komplettansicht(testbrowser):
    select = testbrowser('/campus/article/paginated/komplettansicht').cssselect

    assert len(select('.article-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 0
    # assert len(select('.article-toc')) == 0
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == 'Mehr ZEIT Campus'


def test_article_pagination(testbrowser):
    select = testbrowser('/campus/article/paginated').cssselect
    numbers = select('.article-pager__number')

    assert len(select('.article-header')) == 1
    assert len(select('.page-header')) == 0
    assert len(select('.article-pagination')) == 1
    assert select('.article-pagination__nexttitle')[0].text.strip() == (
        u'Polaroid-Drucker, VR-Brillen, E-Reader, DJ-Kabel und das Hoverboard')
    assert len(numbers) == 7
    assert '--current' in numbers[0].get('class')
    assert numbers[5].text_content().strip() == u'…'
    # assert len(select('.article-toc')) == 1
    # assert len(select('.article-toc__item')) == 5
    # assert '--current' in select('.article-toc__item')[0].get('class')


def test_article_block_citation_should_render_expected_structure(testbrowser):
    browser = testbrowser('/campus/article/citation')
    assert len(browser.cssselect('.quote')) == 3
    assert browser.cssselect('.quote__text')[0].text.startswith(
        u'Es war ein Gedankenanstoß')
    assert browser.cssselect('.quote__source')[0].text_content() == (
        'Ariane Jedlitschka, Kunstschaffende')
    assert browser.cssselect('.quote__link')[0].get('href') == (
        'http://www.imdb.com/title/tt0110912/quotes?item=qt0447099')


def test_article_should_render_topic(testbrowser):
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topic')[0]
    assert tplink.text == 'Science'
    assert tplink.get('href') == 'http://localhost/thema/test'


def test_article_should_have_topic_fallback_label(
        monkeypatch, testbrowser):
    monkeypatch.setattr(zeit.campus.article.Topic, 'label', '')
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topic')[0]
    assert tplink.text == 'Test-Thema'


def test_article_should_not_render_topic_with_missing_fallback_label(
        monkeypatch, testbrowser):
    monkeypatch.setattr(
        zeit.web.campus.view_article.Article, 'topic_label', '')
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topic')
    assert len(tplink) == 0


def test_article_should_not_render_missing_topic(
        monkeypatch, testbrowser):
    monkeypatch.setattr(
        zeit.campus.article.Topic, 'page', None)
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topic')
    assert len(tplink) == 0


def test_article_block_infobox_should_render_expected_structure(testbrowser):
    browser = testbrowser('/campus/article/infobox')
    infobox = browser.cssselect('.infobox')[0]
    assert len(infobox.cssselect('*[role="tab"]')) == 6
    assert len(infobox.cssselect('*[role="tabpanel"]')) == 6


def test_article_block_inlinegallery_should_render_expected_structure(
        testbrowser):
    browser = testbrowser('/campus/article/inline-gallery')
    gallery = browser.cssselect('.inline-gallery')[0]
    assert len(gallery.cssselect('.slide')) == 7


def test_article_tags_are_present(testbrowser):
    browser = testbrowser('/campus/article/simple')
    assert browser.cssselect('nav.article-tags')
    tags = browser.cssselect('a.article-tags__link')
    assert len(tags) == 6
    for tag in tags:
        assert tag.get('rel') == 'tag'


def test_campus_article_renders_video_with_correct_markup(testbrowser):
    bro = testbrowser('/campus/article/video')
    select = bro.cssselect
    assert select(
        'figure.article__item > .video-player#video-player-4193594095001')
    assert select(
        'iframe.video-player__iframe[src*="videoId=4193594095001"]')
    assert select(
        '.video-caption > .video-caption__kicker')[0].text == 'Wearables'
    assert select('.video-caption > .video-caption__title')[0].text == (
        'Verkaufsstart von Apple Watch ohne Warteschlangen')
    assert 'nur auf Vorbestellung ausgegeben wir' in select(
        '.video-caption > .video-caption__description')[0].text


def test_nextread_is_present(testbrowser):
    browser = testbrowser('/campus/article/paginated')
    assert len(browser.cssselect('#nextread')) == 1


def test_article_debate_block_should_render_expected_structure(testbrowser):
    select = testbrowser('/campus/article/debate').cssselect
    assert len(select('.debate')) == 1
    assert len(select('.debate__kicker')) == 1
    assert len(select('.debate__title')) == 1
    assert len(select('.debate__text')) == 1
    assert len(select('.debate__label')) == 1


def test_article_stoa_block_should_render_expected_structure(testbrowser):
    select = testbrowser('/campus/article/stoa').cssselect
    assert len(select('.stoa')) == 1
    assert len(select('.stoa__title')) == 1
    assert len(select('.stoa__link')) == 1
    assert len(select('.stoa__button')) == 1


def test_advertorial_marker_is_present(testbrowser):
    browser = testbrowser('campus/article/advertorial')
    assert len(browser.cssselect('.advertorial-marker')) == 1
    assert len(browser.cssselect('.advertorial-marker__title')) == 1
    assert len(browser.cssselect('.advertorial-marker__text')) == 1


def test_campus_article_does_not_have_contentad(testbrowser):
    select = testbrowser('/campus/article/stoa').cssselect
    assert not select('#iq-artikelanker')


def test_article_has_sharing_bar(testbrowser):
    browser = testbrowser('campus/article/paginated')
    assert len(browser.cssselect('.article-interactions')) == 1
    assert len(browser.cssselect('.sharing-menu')) == 1
    assert len(browser.cssselect('.sharing-menu__item')) == 3
    assert len(browser.cssselect('.print-menu')) == 1


def test_article_header_default_considers_image_layout(testbrowser):
    browser = testbrowser('/campus/article/simple')
    header = browser.cssselect('.article-header--default-no-image')
    assert len(header) == 1

    # default layout "large" should use variant 'portrait'
    browser = testbrowser('/campus/article/paginated')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--portrait')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-variant') == 'portrait'

    # layout "zco-portrait" should use variant 'portrait'
    browser = testbrowser('/campus/article/common')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--portrait')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-variant') == 'portrait'

    # layout "zco-wide" should use variant 'wide'
    browser = testbrowser('/campus/article/header-image-landscape')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--wide')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-variant') == 'wide'


def test_article_has_print_pdf_function(testbrowser):
    browser = testbrowser('/campus/article/debate')
    links = browser.cssselect('.print-menu__link')
    assert (links[0].attrib['href'].endswith(
        '/campus/article/debate?print'))
    assert (links[1].attrib['href'] ==
            'http://pdf.zeit.de/campus/article/debate.pdf')


def test_multi_page_article_has_print_link(testbrowser):
    browser = testbrowser('/campus/article/paginated')
    links = browser.cssselect('.print-menu__link')
    assert (links[0].attrib['href'].endswith(
        '/campus/article/paginated/komplettansicht?print'))


def test_breadcrumbs_for_article(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    view = zeit.web.campus.view_article.Article(context, dummy_request)

    breadcrumbs = [
        ('ZEIT Campus', 'http://xml.zeit.de/campus/index'),
        (u'Beratung: Hier gibt es Hilfe', None)
    ]

    assert view.breadcrumbs == breadcrumbs


def test_breadcrumbs_for_paginated_article_page(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/paginated')
    request = dummy_request
    view = zeit.web.campus.view_article.ArticlePage(context, request)
    view.request.path_info = u'campus/article/paginated/seite-3'

    breadcrumbs = [
        ('ZEIT Campus', 'http://xml.zeit.de/campus/index'),
        (u'Die dritte Seite', u'http://xml.zeit.de/campus/article/paginated')
    ]

    assert view.breadcrumbs == breadcrumbs
