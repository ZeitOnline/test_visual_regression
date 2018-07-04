# -*- coding: utf-8 -*-
import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import zeit.edit.interfaces
import zeit.content.article.edit
import zeit.cms.interfaces
import lxml.etree
import requests
import mock


def test_zar_article_single_page_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/simple').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_full_view_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/paginated/komplettansicht').cssselect

    assert len(select('.summary, .byline, .metadata')) == 2
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_paginated_has_toc(testbrowser):
    browser = testbrowser('/arbeit/article/paginated/')
    toc = browser.cssselect('.article-toc')
    assert len(toc) == 1


def test_zar_article_renders_quotes_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/quotes')
    quotes = browser.cssselect('.quote')
    sources = browser.cssselect('.quote__source')
    assert len(quotes) == 4
    assert len(sources) == 2


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_zar_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'arbeit/article/paginated',
        'arbeit/article/paginated/seite-2',
        'arbeit/article/paginated/komplettansicht',
        'arbeit/article/simple'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


def test_zar_article_zplus_comments_under_register_article(testbrowser):
    c1_param = '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.paragraph--faded')) == 1
    assert len(browser.cssselect('.gate')) == 1
    assert len(browser.cssselect('.comment-section')) == 1


def test_zar_article_zplus_comments_not_under_abo_article(testbrowser):
    c1_param = '?C1-Meter-Status=always_paid'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.comment-section')) == 0


def test_zar_article_paginated_has_headerimage_only_on_first_page(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden')
    assert len(browser.cssselect('div[data-ct-row="headerimage"] img')) == 1
    assert len(browser.cssselect('.article-body .article__media img')) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-2')
    assert not browser.cssselect('div[data-ct-row="headerimage"]')
    assert len(browser.cssselect('.article-body .article__media img')) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-3')
    assert not browser.cssselect('div[data-ct-row="headerimage"]')
    assert len(browser.cssselect('.article-body .article__media img')) == 1

    browser = testbrowser(
        '/arbeit/article/01-digitale-nomaden/komplettansicht')
    assert len(browser.cssselect('div[data-ct-row="headerimage"] img')) == 1


def test_zar_article_image_has_caption(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden')
    headerimage = browser.cssselect('div[data-ct-row="headerimage"]')
    assert len(headerimage) == 1
    headerimage_caption = headerimage[0].cssselect('.figure__text')
    assert len(headerimage_caption) == 1
    assert headerimage_caption[0].text.strip().startswith('Freiheit')


def test_zar_article_toc_has_fallback_title(testbrowser):
    browser = testbrowser('/arbeit/article/paginated-nopagetitle/seite-2')

    toc_items = browser.cssselect('.article-toc__item')
    assert len(toc_items) == 4

    toc_item_1 = toc_items[0].cssselect('span')[0]
    assert toc_item_1.text.strip() == 'Mehrseitiger Artikel ohne Seiten-Titel'

    toc_item_2 = toc_items[1].cssselect('span')[0]
    assert toc_item_2.text.strip() == 'Seite 2'


def test_zar_article_with_dark_header_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark')
    # we want to see one header, which has a modifier
    assert len(browser.cssselect('.article-header--dark')) == 1
    # the article heading items are inside the header-container
    assert len(browser.cssselect(
        '.article-header--dark > .article-heading')) == 1
    # image should be outside/behind the header (because the figure caption
    # has a bright background)
    assert len(browser.cssselect(
        '.article-header--dark + div[data-ct-row="headerimage"]')) == 1


def test_zar_article_header_on_second_page_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark/seite-2')
    assert len(browser.cssselect('.article-header--dark')) == 1
    assert len(browser.cssselect(
        '.article-header--dark .article__page-teaser')) == 1
    assert len(browser.cssselect('div[data-ct-row="headerimage"]')) == 0


def test_zar_article_renders_nextread_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/simple-nextread')
    assert len(browser.cssselect('.nextread')) == 1
    assert len(browser.cssselect('.nextread__lead')) == 1
    assert len(browser.cssselect('.nextread__media')) == 1
    assert len(browser.cssselect('.nextread .series-label')) == 1
    assert len(browser.cssselect('.nextread__kicker')) == 1
    assert len(browser.cssselect('.nextread__title')) == 1
    assert len(browser.cssselect('.nextread__byline')) == 1
    assert len(browser.cssselect('.nextread__text')) == 0


def test_zar_article_renders_nextread_without_fallback_image(testbrowser):
    browser = testbrowser('/arbeit/article/simple-nextread-noimage')
    assert len(browser.cssselect('.nextread__media')) == 0


def test_zar_article_nextread_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
    driver.get(url.format(('/arbeit/article/simple-nextread')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.nextread')))
    except TimeoutException:
        assert False, 'nextread must be present'

    link = driver.find_element_by_css_selector('.nextread__combined-link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.articlebottom.editorial-nextread...text')


def test_zar_article_advertising_nextread_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
    driver.get(url.format(('/arbeit/article/simple-verlagsnextread')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.nextread-advertisement__button')))
    except TimeoutException:
        assert False, 'nextread-advertisement must be present'

    link = driver.find_element_by_css_selector(
        '.nextread-advertisement__button')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.articlebottom.publisher-nextread.button.1.jobs_finden')


def test_zar_article_series_header_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
    driver.get(url.format(('/arbeit/article/series')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.article-series__heading')))
    except TimeoutException:
        assert False, 'Series ZAR article shoul render series header'
    link = driver.find_element_by_css_selector(
        '.article-series__heading')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.articleheader.series...70_jahre_die_zeit')


def test_zar_article_podcast_header_renders_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/podcast')
    assert len(browser.cssselect('.article-heading--podcast')) == 1
    assert len(browser.cssselect('.article-heading__container')) == 1
    assert len(browser.cssselect('.article-heading__headline--podcast')) == 1
    assert len(browser.cssselect('.article-heading__series--podcast')) == 1
    assert len(browser.cssselect('.article-heading__kicker--podcast')) == 1
    assert len(browser.cssselect('.article-heading__title--podcast')) == 1
    assert len(browser.cssselect('.article-heading__podcast-player')) == 1
    assert len(browser.cssselect('.podcastfooter__serieslink')) == 1

    player = browser.cssselect('script.podigee-podcast-player')[0]
    assert player.get('data-configuration') == 'podigee_player_8111'
    assert '"theme": "zon-minimal"' in browser.contents
    browser = testbrowser('/arbeit/article/podcast-no-series')
    assert not browser.cssselect('.podcastfooter__serieslink')


def test_podcast_header_should_omit_podlove_button_if_no_feeds(testbrowser):
    with mock.patch('zeit.web.core.podigee.Podigee.get_podcast') as podcast:
        podcast.return_value = {}
        browser = testbrowser('/arbeit/article/podcast')
    assert not browser.cssselect('script.podlove-subscribe-button')


def test_zar_article_should_provide_jobboxticker(
        testserver, monkeypatch, file_from_data):

    def myget(url, timeout=1):
        xml = lxml.etree.parse(file_from_data('/jobboxticker/feed.rss'))
        mymock = mock.Mock()
        mymock.content = lxml.etree.tostring(xml)
        return mymock

    monkeypatch.setattr(requests, 'get', myget)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/jobbox-ticker')
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    jobbox_ticker = zeit.web.core.interfaces.IArticleModule(body[1])
    ticker_item = list(jobbox_ticker.items)[0]
    assert 'my_title' == ticker_item.title
    assert 'my_text' == ticker_item.text
    assert 'http://my_landing_page' == jobbox_ticker.landing_page_url


def test_zar_article_should_show_jobboxticker(testbrowser):
    browser = testbrowser('/arbeit/article/jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker-item__title')


def test_zar_article_should_hide_empty_jobboxticker(testbrowser, monkeypatch):

    def myget(url, timeout=1):
        mymock = mock.Mock()
        mymock.content = ''
        return mymock

    monkeypatch.setattr(requests, 'get', myget)
    browser = testbrowser('/arbeit/article/jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker__heading')
    assert not browser.cssselect('.jobbox-ticker-item__container')


def test_zar_column_article_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/column')
    select = browser.cssselect
    assert len(select('.article-header-column')) == 1
    assert len(select('.article-header-column__box')) == 1
    assert len(select('.article-header-column__heading')) == 1
    assert len(select('.article-header-column__kicker')) == 1
    assert len(select('.article-header-column__title')) == 1

    assert len(select('.article-header-column__media')) == 1
    assert len(select(
        '.article-header-column__media figcaption.figcaption--hidden')) == 1

    assert len(select('.summary')) == 1
    assert len(select('.metadata')) == 1

    # We set our own byline on unusual position, and suppress the default one
    assert len(select('.article-header-column__byline')) == 1
    assert len(select('.byline')) == 0


def test_zar_column_article_has_correct_structure_on_page2(testbrowser):
    browser = testbrowser('/arbeit/article/column/seite-2')
    select = browser.cssselect
    assert len(select('.article-header-column')) == 1
    assert len(select('.article-header-column__box')) == 1
    assert len(select('.article-header-column__heading')) == 1
    assert len(select('.article-header-column__kicker')) == 1
    assert len(select('.article-header-column__title')) == 1

    assert len(select('.article-header-column__media')) == 1
    assert len(select(
        '.article-header-column__media figcaption.figcaption--hidden')) == 1

    assert len(select('.summary')) == 0
    assert len(select('.metadata')) == 0

    assert len(select('.article__page-teaser')) == 1

    # We set our own byline on unusual position, and suppress the default one
    assert len(select('.article-header-column__byline')) == 1
    assert len(select('.byline')) == 0


def test_zar_profilebox_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/profilebox')
    select = browser.cssselect
    assert len(select('.profilebox')) == 1
    assert len(select('.profilebox__container')) == 1
    assert len(select('.profilebox__title')) == 1
    assert len(select('.profilebox__subtitle')) == 1
    assert len(select('.profilebox__text')) == 1

    assert len(select('.profilebox__media--tablet-desktop')) == 1
    assert len(select('.profilebox__media')) == 1

    # TOC should be behint profilebox
    assert len(select('.profilebox + .article-toc')) == 1


def test_zar_profilebox_should_show_correct_images_per_viewport(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/article/profilebox' % testserver.url)

    teaser_image_mobile = driver.find_element_by_class_name(
        'profilebox__media')
    teaser_image_desktop = driver.find_element_by_class_name(
        'profilebox__media--tablet-desktop')

    assert teaser_image_mobile.is_displayed() is True
    assert teaser_image_desktop.is_displayed() is False

    driver.set_window_size(1000, 480)

    assert teaser_image_mobile.is_displayed() is False
    assert teaser_image_desktop.is_displayed() is True


def test_zar_profilebox_should_toggle_text_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/arbeit/article/profilebox' % testserver.url)

    text_switch = driver.find_element_by_class_name(
        'profilebox__text-switch')
    text_content = driver.find_element_by_class_name(
        'profilebox__text-content')

    # on mobile, we see a switch which reveals the text on click.
    # after that, the switch disappears and you cannot hide the text.
    assert text_content.is_displayed() is False
    assert text_switch.is_displayed() is True

    text_switch.click()
    assert text_switch.is_displayed() is False
    assert text_content.is_displayed() is True

    # on desktop, we see the text (and no switch)
    driver.set_window_size(1200, 800)
    assert text_switch.is_displayed() is False
    assert text_content.is_displayed() is True


def test_zar_advertorial_marker_is_present(testbrowser):
    browser = testbrowser('/arbeit/article/advertorial')
    assert len(browser.cssselect('.advertorial-marker')) == 1
    assert len(browser.cssselect('.advertorial-marker__title')) == 1
    assert len(browser.cssselect('.advertorial-marker__text')) == 1


def test_zar_article_underline_is_applied_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/simple')
    select = browser.cssselect
    assert len(select('.article-heading__title--underlined-skip')) == 1
    assert len(select('.article-heading__title--underlined')) == 0

    # article-headlines in advertorials should not use the underline-hack
    # like usual ZAR aricles do
    browser = testbrowser('/arbeit/article/advertorial')
    assert len(select('.article-heading__title--underlined-skip')) == 0
    assert len(select('.article-heading__title--underlined')) == 1


def test_zar_advertorial_has_no_home_button_as_pagination(testbrowser):
    browser = testbrowser('/arbeit/article/advertorial-onepage')
    assert len(browser.cssselect('.article-pagination__link')) == 0


def test_zar_sharequote_is_hidden_if_toggle_is_false(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('arbeit_quote_sharing')
    browser = testbrowser('/arbeit/article/sharequote')
    assert len(browser.cssselect('.quote-sharing')) == 0


def test_zar_sharequote_is_shown_if_toggle_is_true(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('arbeit_quote_sharing')
    browser = testbrowser('/arbeit/article/sharequote')
    assert len(browser.cssselect('.quote-sharing')) == 2


def test_zar_sharebert_toggle_works(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset(
        'share_blocks_via_screenshot')
    browser = testbrowser('/arbeit/article/sharequote')
    assert len(browser.cssselect('.js-shareblock')) == 0

    zeit.web.core.application.FEATURE_TOGGLES.set(
        'share_blocks_via_screenshot')
    browser = testbrowser('/arbeit/article/sharequote')
    assert len(browser.cssselect('.js-shareblock')) == 2


def test_zar_sharebert_has_correct_attributes(testbrowser):
    browser = testbrowser('/arbeit/article/sharequote/komplettansicht')
    shareblock_links = browser.cssselect(
        '.js-shareblock .quote-sharing__link--twitter')
    assert len(shareblock_links) == 3

    sharelink = shareblock_links[2]
    assert sharelink.attrib['data-sharebert-screenshot-target'].endswith(
        '/arbeit/article/sharequote/module/17/sharequote')
    assert sharelink.attrib['data-sharebert-redirect-url'].endswith(
        '/arbeit/article/sharequote?wt_zmc=sm.ext.zonaudev.twitter.ref.'
        'zeitde.share.link.x&utm_medium=sm&utm_source=twitter_zonaudev'
        '_ext&utm_campaign=ref&utm_content=zeitde_share_link_x')


def test_zar_sharequote_renders_standalone(testbrowser):
    browser = testbrowser('/arbeit/article/sharequote/module/17/sharequote')
    assert browser.cssselect('.quote__text')
    # make sure this is not a whole page
    assert not browser.cssselect('nav')
    assert not browser.cssselect('article')


def test_zar_series_without_series_image_have_correct_series_header_styles(
        testbrowser):
    browser = testbrowser('/arbeit/article/series-no-image')
    assert len(browser.cssselect('.article-series--has-image')) == 0


def test_zar_series_has_series_header(testbrowser):
    browser = testbrowser('/arbeit/article/series')
    assert len(browser.cssselect('.article-series')) == 1


def test_zar_column_has_series_header(testbrowser):
    browser = testbrowser('/arbeit/article/column')
    assert len(browser.cssselect('.article-series')) == 1


def test_zar_podcast_has_no_series_header(testbrowser):
    browser = testbrowser('/arbeit/article/podcast')
    assert len(browser.cssselect('.article-series')) == 0


def test_zar_article_debate_block_renders_expected_structure(testbrowser):
    select = testbrowser('/arbeit/article/debate').cssselect
    assert len(select('.debatebox-on-article')) == 1
    assert len(select('.debatebox-on-article__kicker')) == 1
    assert len(select('.debatebox-on-article__title')) == 1
    assert len(select('.debatebox-on-article__text')) == 1
    assert len(select('.debatebox-on-article__button')) == 1


def test_zar_canonical_url_should_contain_first_page_on_full_view(testbrowser):
    browser = testbrowser('/arbeit/article/paginated/komplettansicht')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('arbeit/article/paginated')


def test_zar_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/arbeit/article/simple'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')

    assert dates[0].text == u'1. Juni 2015, 17:12 Uhr'
    assert len(dates) == 1


def test_zar_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/arbeit/article/simple-modified'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')

    assert dates[0].text == u'1. Juni 2015, 17:12 Uhr'
    assert dates[1].text == u'Aktualisiert am 26. April 2018, 13:49 Uhr'
    assert len(dates) == 2


def test_zar_print_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/arbeit/article/simple-print'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'1. April 2017'
    assert source.text == u'DIE ZEIT Nr. 14/2017, 30. März 2017'
    assert len(dates) == 1


def test_zar_print_changed_article_has_correct_meta_line(
        testserver, selenium_driver):
    selenium_driver.get('{}/arbeit/article/simple-print-modified'.format(
        testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == '1. April 2017, 17:12 Uhr'
    assert dates[1].text == 'Editiert am 26. April 2017, 13:49 Uhr'
    assert source.text == u'DIE ZEIT Nr. 14/2017, 30. März 2017'
    assert len(dates) == 2


def test_zar_article_sourcecode_doesnt_contain_creation_date(testbrowser):
    select = testbrowser('/arbeit/article/simple-modified').cssselect
    dates = select('.metadata__date')
    assert dates[0].text == '26. April 2018, 13:49 Uhr'
    assert dates[1].text == 'Aktualisiert am 26. April 2018, 13:49 Uhr'


def test_zar_print_article_sourcecode_doesnt_contain_date_print_published(
        testbrowser):
    select = testbrowser('/arbeit/article/simple-print-modified').cssselect
    dates = select('.metadata__date')
    source = select('.metadata__source')
    assert dates[0].text == '26. April 2017, 13:49 Uhr'
    assert dates[1].text == 'Editiert am 26. April 2017, 13:49 Uhr'
    assert source[0].text == u'DIE ZEIT Nr. 14/2017'


def test_article_contains_authorbox(testbrowser):
    browser = testbrowser('/arbeit/article/authorbox')
    authorbox = browser.cssselect('.authorbox')
    assert len(authorbox) == 5

    # test custom biography
    author = authorbox[0]
    description = author.cssselect('.authorbox__summary')[0]
    assert description.text.strip() == 'Text im Feld Kurzbio'
    assert description.get('itemprop') == 'description'

    # test author content and microdata
    author = authorbox[2]
    image = author.cssselect('[itemprop="image"]')[0]

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.get('itemscope') is not None
    assert image.cssselect('[itemprop="url"]')[0].get('content').startswith(
        'http://localhost/autoren/B/Jochen_Bittner/jochen-bittner-2/portrait')
    assert author.cssselect('.authorbox__name')[0].text == 'Jochen Bittner'
    assert author.cssselect('[itemprop="description"]')[0].text.strip() == (
        'Redakteur im Ressort Politik, DIE ZEIT.')
    assert author.cssselect('a.authorbox__button')[0].get('href') == (
        'http://localhost/autoren/B/Jochen_Bittner/index.xml')


def test_article_has_valid_twitter_meta_tags(testbrowser):
    select = testbrowser('/arbeit/article/column').metaselect

    assert select('[name="twitter:card"]') == 'summary_large_image'
    assert select('[name="twitter:site"]') == '@zeitonline'
    assert select('[name="twitter:creator"]') == '@wandelderarbeit'
    assert select('[name="twitter:title"]') == (
        u'Chat: Wir rauchen nicht, wir tippen.')
    assert select('[name="twitter:description"]').startswith(
        u'Sommerregen ist sehr gefährlich.')
    assert select('[name="twitter:image"]') == (
        'http://localhost/zeit-online/cp-content/author_images/Julia_Zange/'
        'wide__1300x731')


def test_article_has_valid_facebook_meta_tags(testbrowser):
    select = testbrowser('/arbeit/article/column').metaselect

    assert select('[property="og:site_name"]') == 'ZEIT ONLINE Arbeit'
    assert select('[property="fb:app_id"]') == '638028906281625'
    assert select('[property="fb:pages"]') == (
        '37816894428, 63948163305, 327602816926, 114803848589834')
    assert select('[property="og:type"]') == 'article'
    assert select('[property="og:title"]') == (
        u'Chat: Wir rauchen nicht, wir tippen.')
    assert select('[property="og:description"]').startswith(
        u'Sommerregen ist sehr gefährlich.')
    assert select('[property="og:url"]') == (
        'http://localhost/arbeit/article/column')
    assert select('[property="og:image"]') == (
        'http://localhost/zeit-online/cp-content/author_images/Julia_Zange/'
        'wide__1300x731')
    assert select('[property="og:image:width"]') == '1300'
    assert select('[property="og:image:height"]') == '731'
