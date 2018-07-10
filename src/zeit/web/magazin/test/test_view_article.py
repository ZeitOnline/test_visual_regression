# -*- coding: utf-8 -*-
import datetime

import mock
import pytest
import pytz

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
    portraitbox = page.cssselect('.portraitbox')
    raw = page.cssselect('.raw')

    assert len(paragraph) == 9
    assert 'paragraph article__item' in paragraph[0].get('class')

    assert len(intertitle) == 5
    assert 'article__subheading article__item' in intertitle[0].get('class')

    assert len(portraitbox) == 1
    assert len(raw) == 1

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
    summary = browser.cssselect('.header-article__subtitle')[0]
    authors = summary.cssselect('span[itemtype="http://schema.org/Person"]')
    link = authors[0].cssselect('a[itemprop="url"]')[0]
    assert ' '.join(summary.text_content().strip().split()).endswith(
        'Ein Kommentar von Anne Mustermann, Berlin und Oliver Fritsch, London')
    assert len(authors) == 2
    assert authors[0].text_content().strip() == 'Anne Mustermann'
    assert authors[1].text_content().strip() == 'Oliver Fritsch'
    assert link.get('href') == 'http://localhost/autoren/anne_mustermann'
    assert link.text_content().strip() == 'Anne Mustermann'


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


def isoformat(date):
    return date.replace(microsecond=0).isoformat()


def test_longform_article_has_correct_dates(application):
    # updated longform article
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/05')
    view = zeit.web.magazin.view_article.LongformArticle(context, mock.Mock())
    assert view.show_date_format == 'short'
    assert isoformat(view.date_first_released) == '2013-10-24T08:00:00+02:00'
    assert isoformat(view.date_last_modified) == '2013-11-03T08:10:00+01:00'
    assert view.last_modified_label == 'editiert am 3. November 2013, 8:10 Uhr'


def test_article_has_correct_dates(application):
    # online article, unchanged
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/03')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.show_date_format == 'long'
    assert isoformat(view.date_first_released) == '2013-07-30T17:20:50+02:00'
    assert isoformat(view.date_last_modified) == '2013-07-30T17:20:50+02:00'
    assert not view.last_modified_label


def test_modified_article_has_correct_dates(application):
    # online article, updated
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/10')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.show_date_format == 'long'
    assert isoformat(view.date_first_released) == '2014-02-19T11:41:36+01:00'
    assert isoformat(view.date_last_modified) == '2014-02-20T17:59:41+01:00'
    assert view.last_modified_label == (
        'zuletzt aktualisiert am 20. Februar 2014, 17:59 Uhr')


def test_print_article_has_correct_dates(application):
    # print article, unchanged
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/zplus-zmo-register')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.show_date_format == 'short'
    assert isoformat(view.date_first_released) == '2016-12-20T06:49:02+01:00'
    assert isoformat(view.date_last_modified) == '2016-12-20T06:49:02+01:00'
    assert not view.last_modified_label


def test_modified_print_article_has_correct_dates(application):
    # print article, updated
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.show_date_format == 'long'
    assert isoformat(view.date_first_released) == '2014-02-19T13:53:04+01:00'
    assert isoformat(view.date_last_modified) == '2014-03-04T14:35:24+01:00'
    assert view.last_modified_label == u'editiert am 4. März 2014, 14:35 Uhr'


@pytest.mark.parametrize('released, modified', [
    (datetime.datetime(2014, 1, 1, tzinfo=pytz.UTC), None),
    (datetime.datetime(2014, 1, 1, tzinfo=pytz.UTC),
     datetime.datetime(2014, 5, 2, tzinfo=pytz.UTC))])
def test_date_published_should_be_obfuscated_for_modified_content(
        modified, released, dummy_request, tplbrowser):

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/03')
    view = zeit.web.magazin.view_article.Article(context, dummy_request)

    info = zeit.cms.workflow.interfaces.IPublishInfo(context)
    info.date_last_published_semantic = modified
    info.date_first_released = released

    browser = tplbrowser(
        'zeit.web.magazin:templates/content.html',
        view=view, request=dummy_request)

    dates = browser.cssselect('.meta__date')

    if modified:
        assert dates[0].get('datetime') == isoformat(
            modified.astimezone(pytz.timezone('Europe/Berlin')))
        assert 'encoded-date' in dates[0].get('class')
        assert dates[1].text == 'zuletzt aktualisiert am 2. Mai 2014, 2:00 Uhr'
    else:
        assert dates[0].get('datetime') == isoformat(
            released.astimezone(pytz.timezone('Europe/Berlin')))
        assert 'encoded-date' not in dates[0].get('class')
        assert not dates[1].text


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


def test_article_header_briefmarke_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-briefmarke')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Von Oliver Fritsch')


def test_article_header_column_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-column')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()) == (
        'Von Oliver Fritsch')


def test_article_header_default_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-default')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Von Oliver Fritsch')


def test_article_header_leinwand_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-leinwand')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Eine Glosse von Oliver Fritsch')


def test_article_header_mode_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-mode')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Ein Kommentar von Anne Mustermann')


def test_article_header_text_only_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-text-only')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Interview: Anne Mustermann')


def test_article_header_traum_has_byline(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-traum')
    author = browser.cssselect('main header *[data-ct-row="author"]')
    assert ' '.join(author[0].text_content().strip().split()).endswith(
        'Von Oliver Fritsch')


def test_canonical_url_should_contain_first_page_on_full_view(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03/komplettansicht')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('zeit-magazin/article/03')


def test_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/03'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == '30. Juli 2013, 17:20 Uhr'
    assert dates[0].get_attribute('datetime') == '2013-07-30T17:20:50+02:00'
    assert not dates[1].text
    assert dates[1].get_attribute('datetime') == '2013-07-30T17:20:50+02:00'
    assert not source


def test_modified_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/10'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == (
        '19. Februar 2014, 11:41 Uhr')
    assert dates[0].get_attribute('datetime') == '2014-02-20T17:59:41+01:00'
    assert dates[1].get_attribute('textContent') == (
        'zuletzt aktualisiert am 20. Februar 2014, 17:59 Uhr')
    assert dates[1].get_attribute('datetime') == '2014-02-20T17:59:41+01:00'
    assert source[0].get_attribute('textContent') == 'Erschienen bei golem.de'


def test_print_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/zplus-zmo-register'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == '20. Dezember 2016'
    assert dates[0].get_attribute('datetime') == '2016-12-20T06:49:02+01:00'
    assert not dates[1].text
    assert dates[1].get_attribute('datetime') == '2016-12-20T06:49:02+01:00'
    assert source[0].get_attribute('textContent') == u'ZEITmagazin Nr. 49/2014'


def test_modified_print_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/09'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == (
        '19. Februar 2014, 13:53 Uhr')
    assert dates[0].get_attribute('datetime') == '2014-03-04T14:35:24+01:00'
    assert dates[1].get_attribute('textContent') == (
        u'editiert am 4. März 2014, 14:35 Uhr')
    assert dates[1].get_attribute('datetime') == '2014-03-04T14:35:24+01:00'
    assert source[0].get_attribute('textContent') == u'ZEITmagazin Nr. 26/2008'


def test_longform_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/06'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == '24. Oktober 2013'
    assert dates[0].get_attribute('datetime') == '2013-10-24T08:00:00+02:00'
    assert not dates[1].text
    assert dates[1].get_attribute('datetime') == '2013-10-24T08:00:00+02:00'
    assert not source


def test_modified_longform_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/zeit-magazin/article/07'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == '24. Oktober 2013'
    assert dates[0].get_attribute('datetime') == '2013-11-03T08:10:00+01:00'
    assert dates[1].get_attribute('textContent') == (
        'editiert am 3. November 2013, 8:10 Uhr')
    assert dates[1].get_attribute('datetime') == '2013-11-03T08:10:00+01:00'
    assert source[0].get_attribute('textContent') == u'DIE ZEIT Nr. 44/2013'


def test_gallery_has_correct_meta_line(selenium_driver, testserver):
    selenium_driver.get('{}/galerien/fs-desktop-schreibtisch-computer'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.meta__date')
    source = selenium_driver.find_elements_by_css_selector('.meta__source')

    assert dates[0].get_attribute('textContent') == '2. April 2014, 17:30 Uhr'
    assert dates[0].get_attribute('datetime') == '2014-04-03T16:17:49+02:00'
    assert dates[1].get_attribute('textContent') == (
        'zuletzt aktualisiert am 3. April 2014, 16:17 Uhr')
    assert dates[1].get_attribute('datetime') == '2014-04-03T16:17:49+02:00'
    assert not source
