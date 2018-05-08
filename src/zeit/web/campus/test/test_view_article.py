# -*- coding: utf-8 -*-
import pytest

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
    link = select('.article-pagination__link')[0].get('href')
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
        'figure.article__item > .video-player#video-player-3035864892001')
    assert select(
        'video[data-video-id="3035864892001"]')
    assert select(
        '.video-caption > .video-caption__kicker')[0].text == 'Reporter On Ice'
    assert select('.video-caption > .video-caption__title')[0].text == (
        u'ZEIT ONLINE-Sportreporter Christian Spiller übt Skispringen')
    assert 'in Sotschi probieren wir Wintersportarten selbst aus' in select(
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


def test_campus_article_has_sharing_menu(testbrowser):
    browser = testbrowser('/campus/article/simple')
    sharing_menu = browser.cssselect('.sharing-menu')[0]
    links = sharing_menu.cssselect('.sharing-menu__link')
    labels = sharing_menu.cssselect('.sharing-menu__text')

    assert len(sharing_menu.cssselect('.sharing-menu__item')) == 6
    assert labels[0].text == 'Facebook'
    assert labels[1].text == 'Twittern'
    assert labels[2].text == 'Flippen'
    assert 'via=zeitcampus' in links[1].get('href')


def test_article_header_default_considers_image_layout(testbrowser):
    browser = testbrowser('/campus/article/simple')
    header = browser.cssselect('.article-header--default-no-image')
    assert len(header) == 1

    # default layout "large" should use variant 'portrait'
    browser = testbrowser('/campus/article/paginated')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--portrait')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-ratio') == '0.75'

    # layout "zco-portrait" should use variant 'portrait'
    browser = testbrowser('/campus/article/common')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--portrait')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-ratio') == '0.75'

    # layout "zco-wide" should use variant 'wide'
    browser = testbrowser('/campus/article/header-image-landscape')
    header = browser.cssselect('.article-header--default-with-image')[0]
    figure = header.cssselect('.article-header__media--wide')[0]
    image = figure.cssselect('img')[0]
    assert image.get('data-ratio') == '1.77777777778'


def test_article_has_print_menu(testbrowser):
    browser = testbrowser('/campus/article/debate')
    links = browser.cssselect('.print-menu')
    assert (links[0].get('href').endswith(
        '/campus/article/debate?print'))


def test_multi_page_article_has_print_menu(testbrowser):
    browser = testbrowser('/campus/article/paginated')
    links = browser.cssselect('.print-menu')
    assert (links[0].get('href').endswith(
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


def test_article_contains_webtrekk_parameter_asset(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/cardstack')
    view = zeit.web.campus.view_article.Article(context, dummy_request)

    assert view.webtrekk['customParameter']['cp27'] == 'cardstack.2/seite-1'


def test_article_header_embed_quiz_has_correct_markup(testbrowser):
    browser = testbrowser('/campus/article/embed-header-quiz')
    header = browser.cssselect('.article-header--embed')
    quiz = header[0].cssselect('.quiz')
    topic = header[0].cssselect('.article-header__topic--embed')
    headline = header[0].cssselect('.article-header__headline--embed')
    info = header[0].cssselect('.article-header__embed-info')

    assert len(header) == 1
    assert len(quiz) == 1
    assert len(topic) == 1
    assert len(headline) == 1
    assert len(info) == 1


def test_article_header_embed_cardstack_has_cardstack(testbrowser):
    browser = testbrowser('/campus/article/embed-header-cardstack')
    header = browser.cssselect('.article-header--embed')
    cardstack = header[0].cssselect('.cardstack')
    assert len(header) == 1
    assert len(cardstack) == 1


def test_cardstack_block_produces_correct_html(testbrowser):
    browser = testbrowser('/campus/article/cardstack')
    block = browser.cssselect('main article .cardstack')
    assert len(block) == 1


def test_article_contains_campus_authorbox(testbrowser):
    browser = testbrowser('/campus/article/authorbox')
    authorbox = browser.cssselect('.authorbox')
    assert len(authorbox) == 3

    # test authorbox without image
    author = authorbox[0]
    figure = author.cssselect('.authorbox__media')
    assert not figure

    # test authorbox with image
    author = authorbox[1]
    figure = author.cssselect('.authorbox__media')
    assert len(figure) == 1

    # test if no link to author page is available
    url = author.cssselect('a[itemprop="url"]')
    assert not url

    # check if mobile and desktop resource are given
    image = figure[0].cssselect('.authorbox__media-item')

    # Mobile Image has aspect ratio of 1
    assert image[0].attrib.get('data-mobile-ratio') == '1.0'

    # Desktop Image has aspect ratio of 16 / 9 = 1.77777777778
    assert image[0].attrib.get('data-ratio') == '1.77777777778'


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'campus/article/paginated',
        'campus/article/paginated/seite-2',
        'campus/article/paginated/komplettansicht',
        'campus/article/column',
        'campus/article/simple'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


def test_campus_advertorial_has_no_home_button_as_pagination(testbrowser):
    browser = testbrowser('/campus/article/advertorial-onepage')
    assert len(browser.cssselect('.article-pagination__link')) == 0


def test_campus_print_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_print'.format(
        testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert date.text == u'30. März 2017'
    assert source.text == u'DIE ZEIT Nr. 14/2017, 30. März 2017'


def test_campus_print_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_print_changed'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'30. März 2017, 11:13 Uhr'
    assert dates[1].text == u'Editiert am 31. März 2017, 9:16 Uhr'
    assert source.text == u'DIE ZEIT Nr. 14/2017, 30. März 2017'


def test_campus_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple_date_changed'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')

    assert dates[0].text == u'10. Januar 2016, 10:39 Uhr'
    assert dates[1].text == u'Aktualisiert am 10. Februar 2016, 10:39 Uhr'


def test_campus_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/campus/article/simple'.format(testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')

    assert date.text.strip() == (u'10. Januar 2016, 10:39 Uhr')


def test_canonical_url_should_contain_first_page_on_full_view(testbrowser):
    browser = testbrowser('/campus/article/paginated/komplettansicht')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('campus/article/paginated')


def test_campus_leserarticle_renders_correct_header(testbrowser):
    cssselect = testbrowser('/campus/article/leserartikel').cssselect
    assert cssselect('.article-header--leserartikel')
    assert cssselect('.article-header__topic--leserartikel')
    assert cssselect('.article-header__title--leserartikel')
    assert cssselect('.article-header__leserartikel-info')
    'Ein Leserartikel von' in cssselect('.article-header__byline')[0].text


def test_campus_column_renders_correct_header(testbrowser):
    cssselect = testbrowser('/campus/article/column').cssselect
    assert cssselect('.article-header--column')
    assert cssselect('.article-header__topic--column')
    assert cssselect('.article-header__title--column')
    assert cssselect('.article-header__column-info')
    'Eine Kolumne von' in cssselect('.article-header__byline')[0].text
