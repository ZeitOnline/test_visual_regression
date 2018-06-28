# -*- coding: utf-8 -*-
from StringIO import StringIO
import urllib
import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait
import mock
import pytest

import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.content.article.article

import zeit.web.core.application
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.magazin.view_article


def test_pages_list_contains_blocks(application):
    xml = StringIO("""\
<article>
  <head/>
  <body>
    <division type="page">
      <p>foo bar</p>
    </division>
   <division type="page" teaser="Zweite">
      <p>qux</p>
   </division>
  </body>
</article>
""")
    article = zeit.content.article.article.Article(xml)
    pages = zeit.web.core.article.pages_of_article(article)
    assert 2 == len(pages)
    assert 'foo bar\n' == str(list(pages[0])[0])
    assert 1 == pages[1].number
    assert 'Zweite' == pages[1].teaser


def test_article_has_valid_twitter_meta_tags(testbrowser):
    select = testbrowser('/zeit-magazin/article/01').metaselect

    assert select('[name="twitter:card"]') == 'summary_large_image'
    assert select('[name="twitter:site"]') == '@zeitonline'
    assert select('[name="twitter:creator"]') == '@ZEITmagazin'
    assert select('[name="twitter:title"]') == (
        'Gentrifizierung: Mei, is des traurig!')
    assert select('[name="twitter:description"]') == (
        u'Die Münchner Schoppenstube hat dichtgemacht. Was erzählt uns das '
        u'über die Gentrifizierung? Ein Erklärungsversuch.')
    assert select('[name="twitter:image"]') == ('http://'
        'localhost/exampleimages/artikel/01/schoppenstube/wide__1300x731')


def test_article_has_valid_facebook_meta_tags(testbrowser):
    select = testbrowser('/zeit-magazin/article/01').metaselect

    assert select('[property="og:site_name"]') == 'ZEITmagazin'
    assert select('[property="fb:app_id"]') == '638028906281625'
    assert select('[property="fb:pages"]') == (
        '37816894428, 63948163305, 327602816926, 114803848589834')
    assert select('[property="og:type"]') == 'article'
    assert select('[property="og:title"]') == (
        'Gentrifizierung: Mei, is des traurig!')
    assert select('[property="og:description"]') == (
        u'Die Münchner Schoppenstube hat dichtgemacht. Was erzählt uns das '
        u'über die Gentrifizierung? Ein Erklärungsversuch.')
    assert select('[property="og:url"]') == (
        'http://localhost/zeit-magazin/article/01')
    assert select('[property="og:image"]') == ('http://'
        'localhost/exampleimages/artikel/01/schoppenstube/wide__1300x731')
    assert select('[property="og:image:width"]') == '1300'
    assert select('[property="og:image:height"]') == '731'


@pytest.mark.xfail(reason='tracking scripts & pixels may timeout')
def test_all_tracking_snippets_are_loaded(selenium_driver, testserver):
    selenium_driver.get('%s/zeit-magazin/article/05' % testserver.url)

    def locate_by_selector(xp):
        return WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xp)))

    assert locate_by_selector(
        '//script[@src=\'//stats.g.doubleclick.net/dc.js\']'), (
        'script for Doubleclick not in DOM')
    assert locate_by_selector(
        '//script[@src=\'//www.googletagmanager.com'
        '/gtm.js?id=GTM-TQGX6J\']'), (
        'script for Google tag manager not in DOM')
    assert locate_by_selector(
        '//script[@src=\'http://scripts.zeit.de/js/rsa.js\']'), (
        'script for RSA not in DOM')
    assert locate_by_selector(
        '//script[@src=\'http://scripts.zeit.de/static/js/'
        'webtrekk/webtrekk_v4.0.5.js\']'), (
        'script for Webtrekk not in DOM')
    assert locate_by_selector(
        '//script[@src=\'https://script.ioam.de/iam.js\']'), (
        'script for IVW not in DOM')
    assert locate_by_selector(
        '//img[starts-with(@src,\'http://zeitonl.ivwbox.de\')]'), (
        'pixel for IVW not in DOM')


def test_article03_has_correct_webtrekk_values(httpbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = httpbrowser('/zeit-magazin/article/03')
    source = browser.cssselect(
        'img[src^="https://audev.zeit.de/"]')[0].get('src')
    query = urlparse.parse_qs(urlparse.urlparse(source).query, True)
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()

    # content group
    assert '1: "redaktion",' in webtrekk_config
    assert '2: "article",' in webtrekk_config
    assert '3: "lebensart",' in webtrekk_config
    assert '4: "zede",' in webtrekk_config
    assert '5: "essen-trinken",' in webtrekk_config
    assert '6: "weinkolumne",' in webtrekk_config
    assert '7: "03",' in webtrekk_config
    assert '8: "zeitmz/essenundtrinken/article",' in webtrekk_config
    assert '9: "2013-07-30"' in webtrekk_config

    # custom parameter
    assert '1: "anne mustermann",' in webtrekk_config
    assert '2: "lebensart/essen-trinken/bild-text",' in webtrekk_config
    assert '3: "1/7",' in webtrekk_config
    assert u'4: "wein;italien;toskana;bologna;bozen;florenz;tübingen",' \
        in webtrekk_config
    assert '5: "2013-07-30 17:20:50.176115+02:00",' in webtrekk_config
    assert '6: "4952",' in webtrekk_config
    assert '7: "",' in webtrekk_config
    assert '8: "zede",' in webtrekk_config
    assert '9: "zeitmz/essenundtrinken/article",' in webtrekk_config
    assert '10: "yes",' or '10: "",' in webtrekk_config
    assert '11: "",' in webtrekk_config
    assert '12: window.Zeit.getSiteParam(),' in webtrekk_config
    assert '13: window.Zeit.breakpoint.getTrackingBreakpoint(),' \
        in webtrekk_config
    assert '14: "friedbert"' in webtrekk_config
    assert '15: ""' in webtrekk_config
    assert '25: "original"' in webtrekk_config
    assert '26: "article.column"' in webtrekk_config
    assert '28: "free"' in webtrekk_config
    assert '29: "unfeasible"' in webtrekk_config
    assert '30: "open"' in webtrekk_config

    # noscript string

    page = ('3,redaktion.lebensart.essen-trinken.weinkolumne.article.zede|{}'
            '/zeit-magazin/article/03,0,0,0,0,0,0,0,0').format(
                browser.host.replace('http://', ''))
    assert {k: v[0] for k, v in query.items()} == {
        'p': page,
        'cd': '',
        'cg1': 'redaktion',
        'cg2': 'article',
        'cg3': 'lebensart',
        'cg4': 'zede',
        'cg5': 'essen-trinken',
        'cg6': 'weinkolumne',
        'cg7': '03',
        'cg8': 'zeitmz/essenundtrinken/article',
        'cg9': '2013-07-30',
        'cp1': 'anne mustermann',
        'cp2': 'lebensart/essen-trinken/bild-text',
        'cp3': '1/7',
        'cp4': 'wein;italien;toskana;bologna;bozen;florenz;tübingen',
        'cp5': '2013-07-30 17:20:50.176115+02:00',
        'cp6': '4952',
        'cp7': '',
        'cp8': 'zede',
        'cp9': 'zeitmz/essenundtrinken/article',
        'cp10': 'yes',
        'cp11': '',
        'cp12': 'desktop.site',
        'cp13': 'stationaer',
        'cp14': 'friedbert',
        'cp15': '',
        'cp23': 'nicht_angemeldet',
        'cp25': 'original',
        'cp26': 'article.column',
        'cp27': '',
        'cp28': 'free',
        'cp29': 'unfeasible',
        'cp30': 'open',
        'cp32': 'unfeasible',
        'cp38': 'undefined'}


def test_article03_page2_has_correct_webtrekk_values(httpbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = httpbrowser('/zeit-magazin/article/03/seite-2')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()
    source = browser.cssselect(
        'img[src^="https://audev.zeit.de/"]')[0].get('src')
    query = urlparse.parse_qs(urlparse.urlparse(source).query, True)

    # content group
    assert '7: "seite-2",' in webtrekk_config

    # custom parameter
    assert '3: "2/7",' in webtrekk_config

    # noscript
    page = ('3,redaktion.lebensart.essen-trinken.weinkolumne.article.zede|{}'
            '/zeit-magazin/article/03,0,0,0,0,0,0,0,0').format(
                browser.host.replace('http://', ''))

    assert {k: v[0] for k, v in query.items()} == {
        'p': page,
        'cd': '',
        'cg1': 'redaktion',
        'cg2': 'article',
        'cg3': 'lebensart',
        'cg4': 'zede',
        'cg5': 'essen-trinken',
        'cg6': 'weinkolumne',
        'cg7': 'seite-2',
        'cg8': 'zeitmz/essenundtrinken/article',
        'cg9': '2013-07-30',
        'cp1': 'anne mustermann',
        'cp2': 'lebensart/essen-trinken/bild-text',
        'cp3': '2/7',
        'cp4': 'wein;italien;toskana;bologna;bozen;florenz;tübingen',
        'cp5': '2013-07-30 17:20:50.176115+02:00',
        'cp6': '4952',
        'cp7': '',
        'cp8': 'zede',
        'cp9': 'zeitmz/essenundtrinken/article',
        'cp10': 'yes',
        'cp11': '',
        'cp12': 'desktop.site',
        'cp13': 'stationaer',
        'cp14': 'friedbert',
        'cp15': '',
        'cp23': 'nicht_angemeldet',
        'cp25': 'original',
        'cp26': 'article.column',
        'cp27': '',
        'cp28': 'free',
        'cp29': 'unfeasible',
        'cp30': 'open',
        'cp32': 'unfeasible',
        'cp38': 'undefined'}


def test_cp_has_correct_webtrekk_values(httpbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = httpbrowser('/zeit-magazin/index')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()
    source = browser.cssselect(
        'img[src^="https://audev.zeit.de/"]')[0].get('src')
    query = urlparse.parse_qs(urlparse.urlparse(source).query, True)

    # content group
    assert '1: "redaktion",' in webtrekk_config
    assert '2: "centerpage",' in webtrekk_config
    assert '3: "zeit-magazin",' in webtrekk_config
    assert '4: "zmlb",' in webtrekk_config
    assert '5: "",' in webtrekk_config
    assert '6: "",' in webtrekk_config
    assert '7: "index",' in webtrekk_config
    assert '8: "zeitmz/centerpage",' in webtrekk_config
    assert '9: "2016-04-12"' in webtrekk_config

    # custom parameter
    assert '1: "",' in webtrekk_config
    assert '2: "zeit-magazin/bild-text",' in webtrekk_config
    assert '3: "1/1",' in webtrekk_config
    assert '4: "zeit-magazin",' in webtrekk_config
    assert '5: "2016-05-23 12:14:06.113344+02:00",' in webtrekk_config
    assert '6: "",' in webtrekk_config
    assert '7: "",' in webtrekk_config
    assert '8: "zmlb",' in webtrekk_config
    assert '9: "zeitmz/centerpage",' in webtrekk_config
    assert '10: "yes",' in webtrekk_config
    assert '11: "",' in webtrekk_config
    assert '12: window.Zeit.getSiteParam(),' in webtrekk_config
    assert '13: window.Zeit.breakpoint.getTrackingBreakpoint(),' \
        in webtrekk_config
    assert '14: "friedbert",' in webtrekk_config
    assert '15: "",' in webtrekk_config
    assert '25: "original",' in webtrekk_config
    assert '26: "centerpage.ZMO",' in webtrekk_config
    assert '27: ""' in webtrekk_config
    assert '30: "open"' in webtrekk_config
    assert '28: "free"' in webtrekk_config
    assert '29: "unfeasible"' in webtrekk_config

    page = ('3,redaktion.zeit-magazin...centerpage.zmlb|{}/zeit-magazin/'
            'index,0,0,0,0,0,0,0,0').format(
                browser.host.replace('http://', ''))
    assert {k: v[0] for k, v in query.items()} == {
        'p': page,
        'cd': '',
        'cg1': 'redaktion',
        'cg2': 'centerpage',
        'cg3': 'zeit-magazin',
        'cg4': 'zmlb',
        'cg5': '',
        'cg6': '',
        'cg7': 'index',
        'cg8': 'zeitmz/centerpage',
        'cg9': '2016-04-12',
        'cp1': '',
        'cp2': 'zeit-magazin/bild-text',
        'cp3': '1/1',
        'cp4': 'zeit-magazin',
        'cp5': '2016-05-23 12:14:06.113344+02:00',
        'cp6': '',
        'cp7': '',
        'cp8': 'zmlb',
        'cp9': 'zeitmz/centerpage',
        'cp10': 'yes',
        'cp11': '',
        'cp12': 'desktop.site',
        'cp13': 'stationaer',
        'cp14': 'friedbert',
        'cp15': '',
        'cp23': 'nicht_angemeldet',
        'cp25': 'original',
        'cp26': 'centerpage.ZMO',
        'cp27': '',
        'cp28': 'free',
        'cp29': 'unfeasible',
        'cp30': 'open',
        'cp32': 'unfeasible',
        'cp38': 'undefined'}


def test_webtrekk_series_tag_is_set_corectly(httpbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = httpbrowser('/zeit-magazin/article/06')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()
    source = browser.cssselect(
        'img[src^="https://audev.zeit.de/"]')[0].get('src')

    host = browser.host.replace('http://', '')
    assert ('wt.contentId = "redaktion.zeit-magazin..toedlichekeime'
            '.article.zede|{}/zeit-magazin/article/06";'
            .format(host)) in webtrekk_config
    assert u'6: "tödlichekeime",' in webtrekk_config

    assert ('redaktion.zeit-magazin..toedlichekeime.article.zede%7C'
            '{}/zeit-magazin/article/06,0,0,0,0,0,0,0,0'
            .format(urllib.quote(host))) in source


def test_webtrekk_has_session_parameter(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/slenderized-index?app-content')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()

    assert '1: window.Zeit.wrapped.client' in webtrekk_config


def test_webtrekk_noscript_contains_user_info(httpbrowser):
    with mock.patch('zeit.web.core.security.get_user_info') as get_user:
        get_user.return_value = {
            'ssoid': '123',
            'mail': 'test@example.org',
            'name': 'jrandom',
        }
        browser = httpbrowser('/zeit-magazin/article/03',
                              cookies={'my_sso_cookie': 'just_be_present'})
        webtrekk = browser.cssselect(
            'img[src^="https://audev.zeit.de/"]')[0].get('src')
        assert 'cd=123' in webtrekk


@pytest.mark.xfail(reason='tracking scripts & pixels may timeout')
def test_ivw_tracking_for_mobile_and_desktop_and_wrapper(
        selenium_driver, testserver):

    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules', 'iqd')
    driver = selenium_driver

    # ipad landscape
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/03' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "zeitonl"

    # Wrapper-Apps must always be the »MEW-Angebotskennung« mobzeit
    # we simulate this via the get-param 'appcontent' instead of user-agent
    driver.get('%s/zeit-magazin/article/02?app-content=true' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "mobzeit"

    # ipad portrait and smaller
    driver.set_window_size(766, 1024)
    driver.get('%s/zeit-magazin/article/01' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "mobzeit"


def test_article_has_correct_page_title(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert '<title>Kolumne Die Ausleser:'\
        ' Der Chianti hat eine'\
        ' zweite Chance verdient' in browser.contents


def test_article_without_supertitle_has_correct_page_title(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03a')
    assert '<title>'\
        'Der Chianti hat eine'\
        ' zweite Chance verdient | ZEITmagazin' in browser.contents


def test_article_should_have_correct_seo_title(testbrowser):
    browser = testbrowser('/zeit-magazin/article/04')
    assert '<title>SEO title | ZEITmagazin</title>' in browser.contents


def test_article_has_correct_page_meta_description(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert '<meta name="description" '\
        'content="Erst Heilsbringer, dann Massenware:'\
        ' Der Chianti ist tief gefallen. Doch'\
        ' engagierte Winzer retten dem Wein in der'\
        ' Bastflasche die Ehre. ">' in browser.contents


def test_article_should_have_correct_seo_description(testbrowser):
    browser = testbrowser('/zeit-magazin/article/04')
    assert '<meta name="description" content="SEO description">' \
        in browser.contents


def test_article_has_correct_page_meta_keywords(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert '<meta name="keywords" content="Wein, Italien,'\
        ' Toskana, Bologna, Bozen, Florenz, Tübingen">' in browser.contents


def test_print_article_has_correct_date(testbrowser):
    # not updated print article
    browser = testbrowser('/zeit-magazin/article/08')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == '19. Februar 2014'
    assert not dates[1].text


def test_modified_print_article_has_correct_date(testbrowser):
    # updated print article
    browser = testbrowser('/zeit-magazin/article/09')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == u'4. März 2014, 14:35 Uhr'
    assert dates[1].text == u'editiert am 4. März 2014, 14:35 Uhr'


def test_article_has_correct_date(testbrowser):
    # not updated online article
    browser = testbrowser('/zeit-magazin/article/03')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == '30. Juli 2013, 17:20 Uhr'
    assert not dates[1].text


def test_modified_article_has_correct_date(testbrowser):
    # updated online article
    browser = testbrowser('/zeit-magazin/article/10')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == '20. Februar 2014, 17:59 Uhr'
    assert dates[1].text == (
        'zuletzt aktualisiert am 20. Februar 2014, 17:59 Uhr')


def test_longform_article_has_correct_date(testbrowser):
    # not updated longform
    browser = testbrowser('/zeit-magazin/article/06')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == '24. Oktober 2013'
    assert not dates[1].text


def test_modified_longform_article_has_correct_date(testbrowser):
    # updated longform
    browser = testbrowser('/zeit-magazin/article/07')
    dates = browser.cssselect('.meta__date')
    assert dates[0].text == '3. November 2013'
    assert dates[1].text == 'editiert am 3. November 2013, 8:10 Uhr'


def test_article03_has_no_source(testbrowser):
    # zon source
    browser = testbrowser('/zeit-magazin/article/03')
    assert 'meta__source' not in browser.contents


def test_article10_has_correct_online_source(testbrowser):
    # online source
    browser = testbrowser('/zeit-magazin/article/10')
    meta_source = browser.cssselect('span.meta__source')[0]
    assert 'Erschienen bei golem.de' in meta_source.text_content()


def test_article08_has_correct_print_source(testbrowser):
    # print source
    browser = testbrowser('/zeit-magazin/article/08')
    meta_source = browser.cssselect('span.meta__source')[0]
    assert u'DIE ZEIT Nr. 26/2008' in meta_source.text_content()


def test_article_1_10_produce_no_error(testbrowser):
    assert testbrowser('/zeit-magazin/article/01').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/02').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/03').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/04').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/05').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/06').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/08').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/09').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/10').cssselect(
        'div.article__body')


def test_article_1_10_have_correct_h1(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/02')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/04')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/05')
    assert browser.cssselect('h1 > .article__head__title')
    browser = testbrowser('/zeit-magazin/article/06')
    assert browser.cssselect('h1 > .article__head__title')
    browser = testbrowser('/zeit-magazin/article/08')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/09')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/10')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')


def test_header_articles_produce_no_error(testbrowser):
    assert testbrowser('/zeit-magazin/article/header-default').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/header-traum').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/header-text-only').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/header-briefmarke').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/header-leinwand').cssselect(
        'div.article__body')
    assert testbrowser('/zeit-magazin/article/header-mode').cssselect(
        'div.article__body')


def test_header_articles_have_correct_h1(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-default')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/header-traum')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/header-briefmarke')
    assert browser.cssselect('h1 > .headline__title')
    browser = testbrowser('/zeit-magazin/article/header-leinwand')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')
    browser = testbrowser('/zeit-magazin/article/header-mode')
    assert browser.cssselect('h1 > .headline__title')
    assert browser.cssselect('h1 > .headline__supertitle')


def test_article_header_traum_has_correct_subtitle(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-traum')
    subtitle = browser.cssselect('.header-article__subtitle')[0]
    assert subtitle.text_content().strip() == (
        u'Wie viele Flüchtlingskinder bin ich eine Suchende, Getriebene.')


def test_article_header_default_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-default')
    assert browser.cssselect('header.header-article.header-article--default')


def test_article_header_traum_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-traum')
    assert browser.cssselect('header.header-article.header-article--traum')


def test_article_header_text_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert browser.cssselect('header.header-article.header-article--text-only')


def test_article_header_briefmarke_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-briefmarke')
    assert browser.cssselect(
        'header.header-article.header-article--briefmarke')


def test_article_header_leinwand_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-leinwand')
    assert browser.cssselect('header.header-article.header-article--leinwand')


def test_article_header_mode_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-mode')
    assert browser.cssselect('header.header-article.header-article--mode')


def test_article_header_standardkolumne_should_have_correct_src(testbrowser):
    browser = testbrowser('/zeit-magazin/article/standardkolumne-beispiel')
    assert browser.cssselect('header.header-article.header-article--column')


def test_article_header_sequelpage_should_have_correct_source(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03/seite-2')
    assert browser.cssselect('header.header-article.header-article--sequel')


def test_nextread_teaser_block_has_teasers_available(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert hasattr(nextread, '__iter__'), 'Nextread block should be iterable.'
    assert len(nextread) == 1, '"Artikel 09" has exactly one nextread.'

    def func(a):
        return isinstance(a, zeit.content.article.article.Article)

    assert all(map(func, nextread)), 'All nextread teasers should be articles.'


def test_nextread_teaser_blocks_has_correct_layout_id(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 09" has a base nextread layout.'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/03')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'maximal', \
        '"Artikel 03" has a maximal nextread layout.'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 01" has no nextread layout, should fallback to base.'


def test_nextread_teaser_block_teasers_is_accessable(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert all(teaser for teaser in nextread), \
        'Nextread block should iterate over its teasers.'
    assert nextread[0], \
        'Nextread block should expose its teasers via index.'


def test_nextread_base_layout_has_expected_structure(testbrowser):
    browser = testbrowser('/zeit-magazin/article/09')
    nextread = browser.cssselect('.nextread-base')[0]
    assert len(nextread.cssselect('a')) == 1
    assert len(nextread.cssselect('.nextread-base__media')) == 1
    assert len(nextread.cssselect('.nextread-base__heading')) == 1


def test_nextread_should_fallback_to_default_layout(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/02')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 02" has invalid nextread layout, should fallback to base.'


def test_article_with_images_should_render_image_container(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.cssselect('div.article-page figure.figure-stamp')


def test_article_without_images_should_not_render_image_container(testbrowser):
    browser = testbrowser('/zeit-magazin/article/artikel-ohne-assets')
    assert not browser.cssselect('div.article-page figure.figure-stamp')


def test_article_with_fictitious_imgs_should_not_render_img_container(
        testbrowser):
    browser = testbrowser('/zeit-magazin/article/artikel-mit-fiktiven-assets')
    assert not browser.cssselect('div.article-page figure.figure-stamp')


def test_article_has_linked_image(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.xpath('//a[@href="http://www.test.de"]/img')


def test_article02_should_have_esi_include(testbrowser):
    browser = testbrowser('/zeit-magazin/article/02')
    assert len(browser.cssselect('main include')) == 2


@pytest.mark.parametrize('path, selector', [
    ('/zeit-magazin/article/03', '.figure-stamp .figure__copyright'),
    ('/zeit-magazin/article/05', '.longform-header__copyright'),
    ('/zeit-magazin/article/header-default', '.header-article__copyright')])
def test_article_has_linked_copyright(testbrowser, path, selector):
    browser = testbrowser(path)
    assert browser.cssselect(selector)
    copyright = browser.cssselect(selector)[0]
    assert copyright.get('itemprop') == 'copyrightHolder'
    assert copyright.cssselect('a')
    link = copyright.cssselect('a')[0]
    assert link.get('href') == 'http://foo.de'
    assert link.get('target') == '_blank'
    assert link.text_content() == u'© Reuters/Alessandro Bianchi'


def test_feature_longform_should_have_zon_logo_header(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    assert browser.cssselect('.header__logo--zon')

    link = browser.cssselect('.header__publisher a')[0]
    assert link.get('href') == 'http://localhost/index'


def test_feature_longform_should_have_zon_logo_footer(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    assert browser.cssselect('.main-footer__logo--zon-small')


def test_feature_longform_is_fullwidth(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/zeit-magazin/article/05'.format(
        testserver.url))
    driver.maximize_window()
    width = driver.execute_script(
        'return document.querySelector(".page").offsetWidth')
    window_width = driver.execute_script(
        'return document.documentElement.clientWidth')
    assert width == window_width


def test_feature_longform_should_have_zonish_title(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    title = browser.cssselect('head > title')
    assert 'ZEIT ONLINE' in title[0].text


def test_feature_longform_should_have_zon_twittername(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    creator = browser.cssselect('meta[name="twitter:site"]')
    assert creator[0].values()[1] == '@zeitonline'


def test_feature_longform_has_valid_twitter_meta_tags(testbrowser):
    select = testbrowser('/feature/feature_longform').metaselect

    assert select('[name="twitter:card"]') == 'summary_large_image'
    assert select('[name="twitter:site"]') == '@zeitonline'
    assert select('[name="twitter:creator"]') == '@zeitonline'
    assert select('[name="twitter:title"]') == (
        'Friedhof Hamburg-Ohlsdorf: Die Angst des Friedhofs vor dem Tod')
    assert select('[name="twitter:description"]').startswith(
        u'Gestorben wird immer. Aber nicht mehr genug. Deutschland schrumpft.')
    assert select('[name="twitter:image"]') == (
        'http://localhost/zeit-online/image/s15-einaescherung/wide__1300x731')


def test_feature_longform_has_valid_facebook_meta_tags(testbrowser):
    select = testbrowser('/feature/feature_longform').metaselect

    assert select('[property="og:site_name"]') == 'ZEIT ONLINE'
    assert select('[property="fb:app_id"]') == '638028906281625'
    assert select('[property="fb:pages"]') == (
        '37816894428, 63948163305, 327602816926, 114803848589834')
    assert select('[property="og:type"]') == 'article'
    assert select('[property="og:title"]') == (
        'Friedhof Hamburg-Ohlsdorf: Die Angst des Friedhofs vor dem Tod')
    assert select('[property="og:description"]').startswith(
        u'Gestorben wird immer. Aber nicht mehr genug. Deutschland schrumpft.')
    assert select('[property="og:url"]') == (
        'http://localhost/feature/feature_longform')
    assert select('[property="og:image"]') == (
        'http://localhost/zeit-online/image/s15-einaescherung/wide__1300x731')
    assert select('[property="og:image:width"]') == '1300'
    assert select('[property="og:image:height"]') == '731'


def test_article_view_has_leadtime_set_if_article_provides_it(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/10')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    assert view.leadtime.start
    assert view.leadtime.end


def test_article_view_has_no_leadtime_if_the_attribute_is_missing(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/09')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    assert view.leadtime.start is None
    assert view.leadtime.end is None


def test_advertorial_article_shows_advertorial_marker(testbrowser):
    browser = testbrowser('/zeit-magazin/article/advertorial')
    assert browser.cssselect('.header__ad-label')[0].text == 'Anzeige'
    browser = testbrowser('/zeit-magazin/article/01')
    assert not browser.cssselect('.header__ad-label')


def test_articles_should_have_exact_one_h1(testbrowser):
    assert len(testbrowser('/zeit-magazin/article/01').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/02').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/03').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/04').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/05').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/07').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/08').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/09').cssselect('h1')) == 1
    assert len(testbrowser('/zeit-magazin/article/10').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-default').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-traum').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-text-only').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-briefmarke').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-leinwand').cssselect('h1')) == 1
    assert len(testbrowser(
               '/zeit-magazin/article/header-mode').cssselect('h1')) == 1


def test_longform_should_have_exact_one_h1(testbrowser):
    browser = testbrowser('/zeit-magazin/article/06')
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1


def test_article_first_page_must_have_no_image_as_first_block(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    block = context.body.values()[0]
    assert zeit.content.article.edit.interfaces.IImage.providedBy(
        block), ('Image should be present on first position in '
                 'article body.')
    block = zeit.web.core.article.pages_of_article(context)[0][0]
    assert not zeit.content.article.edit.interfaces.IImage.providedBy(
        block), 'Image must not be present on first position in page.'


def test_zmo_should_not_render_advertisement_nextread(
        testbrowser, workingcopy):
    # /zeit-magazin/article/10 has ressort 'Wirtschaft'
    # which has ad-nextread content.
    browser = testbrowser('/zeit-magazin/article/10')
    assert len(browser.cssselect('.nextread-advertisement')) == 0


def test_article_contains_zeit_clickcounter(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-magazin/article/03')
    counter = browser.cssselect('body noscript img[src^="https://cc.zeit.de"]')
    assert ("img.src = 'https://cc.zeit.de/cc.gif?banner-channel="
            "zeitmz/essenundtrinken/article") in browser.contents
    assert len(counter) == 1
    assert ('cc.zeit.de/cc.gif?banner-channel=zeitmz/essenundtrinken/article'
            ) in counter[0].get('src')


def test_article_tags_are_present_and_limited_in_article(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    tags = browser.cssselect('.article-tags')
    links = tags[0].cssselect('a[rel="tag"]')

    assert len(tags) == 1
    assert len(tags[0].find_class('article-tags__title')) == 1
    assert len(links) == 6


def test_article_tags_are_present_and_limited_in_gallery(testbrowser):
    browser = testbrowser('/galerien/bg-automesse-detroit-2014-usa')
    tags = browser.cssselect('.article-tags')
    links = tags[0].cssselect('a[rel="tag"]')

    assert len(tags) == 1
    assert len(tags[0].find_class('article-tags__title')) == 1
    assert len(links) == 6


def test_article_tags_are_present_and_limited_in_longform(testbrowser):
    browser = testbrowser('/zeit-magazin/article/05')
    tags = browser.cssselect('.article-tags')
    links = tags[0].cssselect('a[rel="tag"]')

    assert len(tags) == 1
    assert len(tags[0].find_class('article-tags__title')) == 1
    assert len(links) == 6


def test_infographics_should_display_header_above_image(testbrowser):
    browser = testbrowser('/zeit-magazin/article/infographic')
    items = list(browser.cssselect('.infographic__media')[0].iterchildren())
    assert 'Die Entschlackung' == items[0].text
    assert (
        u'Potenzial der Bertelsmann-Geschäfte (in Prozent des Umsatzes)' ==
        items[1].text)


def test_share_buttons_are_present(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    canonical = browser.cssselect('link[rel="canonical"]')[0].get('href')
    sharing_menu = browser.cssselect('.sharing-menu')[0]
    links = sharing_menu.cssselect('.sharing-menu__link')
    labels = sharing_menu.cssselect('.sharing-menu__text')

    #  facebook
    parts = urlparse.urlparse(links[0].get('href'))
    query = urlparse.parse_qs(parts.query)
    url = query.get('u').pop(0)
    assert 'wt_zmc=sm.ext.zonaudev.facebook.ref.zeitde.share.link' in url
    assert 'utm_medium=sm' in url
    assert 'utm_source=facebook_zonaudev_ext' in url
    assert 'utm_campaign=ref' in url
    assert 'utm_content=zeitde_share_link_x' in url

    #  twitter
    parts = urlparse.urlparse(links[1].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert query.get('text').pop(0) == (
        'Der Chianti hat eine zweite Chance verdient')
    assert query.get('via').pop(0) == 'ZEITmagazin'
    assert 'share' in query.get('url').pop(0)

    #  flipboard
    parts = urlparse.urlparse(links[2].get('href'))
    query = urlparse.parse_qs(parts.query)
    url = query.get('url').pop(0)
    assert 'wt_zmc=soref.ext.zonaudev.flipboard.ref.zeitde.share.link' in url
    assert query.get('title').pop(0) == (
        'Der Chianti hat eine zweite Chance verdient')

    #  whatsapp
    parts = urlparse.urlparse(links[3].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert ('Der Chianti hat eine zweite Chance verdient - '
            'Artikel auf ZEITmagazin ONLINE: ') in query.get('text').pop(0)

    #  facebook messenger
    parts = urlparse.urlparse(links[4].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert query.get('link').pop(0).startswith(canonical)
    assert query.get('app_id').pop(0) == '638028906281625'

    #  pocket
    parts = urlparse.urlparse(links[5].get('href'))
    query = urlparse.parse_qs(parts.query)
    url = query['url'][0]
    assert 'utm_source=pocket_zonaudev_ext' in url
    assert 'utm_campaign=ref' in url
    assert 'utm_content=zeitde_share_link_x' in url

    #  mail
    parts = urlparse.urlparse(links[6].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert ('Der Chianti hat eine zweite Chance verdient - '
            'Artikel auf ZEITmagazin ONLINE') in query.get('subject').pop(0)
    assert 'Artikel auf ZEITmagazin ONLINE lesen:' in query.get('body').pop(0)

    assert labels[0].text == 'Facebook'
    assert labels[1].text == 'Twittern'
    assert labels[2].text == 'Flippen'
    assert labels[3].text == 'WhatsApp'
    assert labels[4].text == 'Facebook Messenger'
    assert labels[5].text == 'Pocket'
    assert labels[6].text == 'Mailen'


def test_webtrekk_paywall_status_is_set_on_paid_article(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    url = ('/zeit-online/article/zplus-zeit'
           '?C1-Meter-Status=always_paid')
    browser = testbrowser(url)

    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]
    webtrekk_config = script.text_content().strip()
    assert '30: "paid"' in webtrekk_config


def test_magazine_series_should_has_right_site_name(testbrowser):
    browser = testbrowser('/serie/martenstein')
    assert '<meta property="og:site_name" '\
        'content="ZEITmagazin">' in browser.contents
