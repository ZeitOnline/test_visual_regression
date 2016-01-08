# -*- coding: utf-8 -*-
from StringIO import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait
import mock

import zeit.content.article.article
import zeit.cms.interfaces

import zeit.web.core.interfaces
import zeit.web.magazin.view_article

import pytest


def test_ipages_contains_blocks(application):
    xml = StringIO("""\
<article>
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
    pages = zeit.web.core.interfaces.IPages(article)
    assert 2 == len(pages)
    assert 'foo bar\n' == str(list(pages[0])[0])
    assert 1 == pages[1].number
    assert 'Zweite' == pages[1].teaser


def test_article_has_valid_twitter_meta_tags(testbrowser):
    browser = testbrowser('/artikel/01')
    assert (
        '<meta name="twitter:card" content="summary_large_image">'
        in browser.contents)
    assert '<meta name="twitter:site"'\
        ' content="@zeitonline">' in browser.contents
    assert '<meta name="twitter:creator"'\
        ' content="@ZEITmagazin">' in browser.contents
    assert '<meta name="twitter:title"'\
        ' content="Mei, is des traurig!">' in browser.contents
    assert '<meta name="twitter:description"'\
        ' content="Die Münchner Schoppenstube hat dichtgemacht.'\
        ' Was erzählt uns das über die Gentrifizierung?'\
        ' Ein Erklärungsversuch.">' in browser.contents
    assert '<meta name="twitter:image"' in browser.contents


def test_article_has_valid_facebook_meta_tags(testbrowser):
    browser = testbrowser('/artikel/01')
    assert '<meta property="og:site_name" '\
        'content="ZEITmagazin">' in browser.contents
    assert '<meta property="fb:admins"'\
        ' content="595098294">' in browser.contents
    assert '<meta property="og:type"'\
        ' content="article">' in browser.contents
    assert '<meta property="og:title"'\
        ' content="Mei, is des traurig!">' in browser.contents
    assert '<meta property="og:description"'\
        ' content="Die Münchner Schoppenstube hat dichtgemacht.'\
        ' Was erzählt uns das über die Gentrifizierung?'\
        ' Ein Erklärungsversuch.">' in browser.contents
    assert '<meta property="og:image" ' in browser.contents


@pytest.mark.xfail(reason='tracking scripts & pixels may timeout')
def test_all_tracking_snippets_are_loaded(selenium_driver, testserver):
    selenium_driver.get('%s/artikel/05' % testserver.url)

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


def test_article03_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)

    # content _group
    assert '1: "redaktion",' in browser.contents
    assert '2: "article",' in browser.contents
    assert '3: "lebensart",' in browser.contents
    assert '4: "zede",' in browser.contents
    assert '5: "essen-trinken",' in browser.contents
    assert '6: "weinkolumne",' in browser.contents
    assert '7: "03",' in browser.contents
    assert '8: "zeitmz/essenundtrinken/article",' in browser.contents
    assert '9: "2013-07-30"' in browser.contents

    # custom parameter
    assert '1: "anne mustermann",' in browser.contents
    assert '2: "lebensart/essen-trinken/bild-text",' in browser.contents
    assert '3: "1/7",' in browser.contents
    assert '4: "wein;italien;toskana;bologna;bozen;florenz;tübingen",' \
        in browser.contents
    assert '5: "2013-07-30 17:20:50.176115+02:00",' in browser.contents
    assert '6: "4952",' in browser.contents
    assert '7: "",' in browser.contents
    assert '8: "zede",' in browser.contents
    assert '9: "zeitmz/essenundtrinken/article",' in browser.contents
    assert '10: "yes",' or '10: "",' in browser.contents
    assert '11: "",' in browser.contents
    assert '12: window.Zeit.getSiteParam("site"),' in browser.contents
    assert '13: window.Zeit.breakpoint.getTrackingBreakpoint(),' \
        in browser.contents
    assert '14: "alt"' in browser.contents
    assert '15: ""' in browser.contents
    assert '25: "original"' in browser.contents

    # noscript string
    assert ('http://zeit01.webtrekk.net/981949533494636/wt.pl?p=328,redaktion'
            '.lebensart.essen-trinken.weinkolumne.article.zede|{url}/'
            'artikel/03,0,0,0,0,0,0,0,0&amp;cg1=redaktion&amp;cg2=article'
            '&amp;cg3=lebensart&amp;cg4=zede&amp;cg5=essen-trinken&amp;cg6'
            '=weinkolumne&amp;cg7=03&amp;cg8=zeitmz/essenundtrinken/article'
            '&amp;cg9=2013-07-30&amp;cp1=anne mustermann&amp;cp2=lebensart/'
            'essen-trinken/bild-text&amp;cp3=1/7&amp;cp4=wein;italien;'
            'toskana;bologna;bozen;florenz;tübingen&amp;cp5=2013-07-30 '
            '17:20:50.176115+02:00&amp;cp6=4952&amp;cp7=&amp;cp8=zede'
            '&amp;cp9=zeitmz/essenundtrinken/article&amp;cp10=&amp;'
            'cp11=&amp;cp12=desktop'
            '.site').format(url=testserver['http_address']) in browser.contents


def test_article03_page2_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)

    # content _group
    assert '7: "seite-2",' in browser.contents

    # custom parameter
    assert '3: "2/7",' in browser.contents

    # noscript
    assert ('http://zeit01.webtrekk.net/981949533494636/wt.pl?p=328,'
            'redaktion.lebensart.essen-trinken.weinkolumne.article.'
            'zede|{url}/artikel/03,0,0,0,0,0,0,0,0&amp;cg1=redaktion'
            '&amp;cg2=article&amp;cg3=lebensart&amp;cg4=zede&amp;cg5=essen-'
            'trinken&amp;cg6=weinkolumne&amp;cg7=seite-2&amp;cg8=zeitmz/'
            'essenundtrinken/article&amp;cg9=2013-07-30&amp;cp1=anne '
            'mustermann&amp;cp2=lebensart/essen-trinken/bild-text&amp;'
            'cp3=2/7&amp;cp4=wein;italien;toskana;bologna;bozen;florenz;'
            'tübingen&amp;cp5=2013-07-30 17:20:50.176115+02:00&amp;cp6=4952'
            '&amp;cp7=&amp;cp8=zede&amp;cp9=zeitmz/essenundtrinken/article'
            '&amp;cp10=&amp;cp11=&amp;cp12=desktop'
            '.site').format(url=testserver['http_address']) in browser.contents


def test_cp_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert '1: "redaktion",' in browser.contents
    assert '2: "centerpage",' in browser.contents
    assert '3: "lebensart",' in browser.contents
    assert '4: "zede",' in browser.contents
    assert '5: "",' in browser.contents
    assert '6: "",' in browser.contents
    assert '7: "test-cp-zmo",' in browser.contents
    assert '8: "zeitmz/centerpage",' in browser.contents
    assert '9: ""' in browser.contents
    assert ('wt.pl?p=328,redaktion.lebensart...'
            'centerpage.zede|{url}/zeit-magazin/test-cp/test-cp-zmo,'
            '0,0,0,0,0,0,0,0&amp;cg1=redaktion&amp;cg2=centerpage&amp;'
            'cg3=lebensart&amp;cg4=zede&amp;cg5=&amp;cg6=&amp;'
            'cg7=test-cp-zmo&amp;cg8=zeitmz/centerpage&amp;'
            'cg9=').format(url=testserver['http_address']) in browser.contents


def test_webtrekk_series_tag_is_set_corectly(testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/06' % testserver.url)
    assert '6: "tödlichekeime",' in browser.contents
    assert ('redaktion.zeit-magazin..tödlichekeime.'
            'article.zei|{url}/artikel/'
            '06').format(url=testserver['http_address']) in browser.contents


def test_webtrekk_has_session_parameter(testserver, testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index?app-content')
    assert '1: window.Zeit.wrapped.client' in browser.contents


@pytest.mark.xfail(reason='tracking scripts & pixels may timeout')
def test_ivw_tracking_for_mobile_and_desktop_and_wrapper(
        selenium_driver, testserver, monkeypatch):

    def tpm(me):
        return True

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    driver = selenium_driver

    # ipad landscape
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/03' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "zeitonl"

    # Wrapper-Apps must always be the »MEW-Angebotskennung« mobzeit
    # we simulate this via the get-param 'appcontent' instead of user-agent
    driver.get('%s/artikel/02?app-content=true' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "mobzeit"

    # ipad portrait and smaller
    driver.set_window_size(766, 1024)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "mobzeit"


def test_article_has_correct_page_title(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert '<title>Kolumne Die Ausleser:'\
        ' Der Chianti hat eine'\
        ' zweite Chance verdient' in browser.contents


def test_article_without_supertitle_has_correct_page_title(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03a' % testserver.url)
    assert '<title>'\
        'Der Chianti hat eine'\
        ' zweite Chance verdient | ZEITmagazin' in browser.contents


def test_article_should_have_correct_seo_title(testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert '<title>SEO title | ZEITmagazin</title>' in browser.contents


def test_article_has_correct_page_meta_description(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert '<meta name="description" '\
        'content="Erst Heilsbringer, dann Massenware:'\
        ' Der Chianti ist tief gefallen. Doch'\
        ' engagierte Winzer retten dem Wein in der'\
        ' Bastflasche die Ehre. ">' in browser.contents


def test_article_should_have_correct_seo_description(testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert '<meta name="description" content="SEO description">' \
        in browser.contents


def test_article_has_correct_page_meta_keywords(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert '<meta name="keywords" content="Wein, Italien,'\
        ' Toskana, Bologna, Bozen, Florenz, Tübingen">' in browser.contents


def test_article08_has_correct_date(testbrowser):
    # not updated print article
    browser = testbrowser('/artikel/08')
    date = browser.cssselect('.article__head__meta__date')[0].text
    assert date.strip() == '19. Februar 2014'


def test_article09_has_correct_date(testbrowser):
    # updated print article
    browser = testbrowser('/artikel/09')
    date = browser.cssselect('.article__head__meta__date')[0].text
    assert date.strip() == u'4. März 2014, 14:35 Uhr'


def test_article03_has_correct_date(testbrowser):
    # not updated online article
    browser = testbrowser('/artikel/03')
    date = browser.cssselect('.article__head__meta__date')[0].text
    assert date.strip() == '30. Juli 2013, 17:20 Uhr'


def test_article10_has_correct_date(testbrowser):
    # updated online article
    browser = testbrowser('/artikel/10')
    date = browser.cssselect('.article__head__meta__date')[0].text
    assert date.strip() == '20. Februar 2014, 17:59 Uhr'


def test_article05_has_correct_date(testbrowser):
    # longform
    browser = testbrowser('/artikel/05')
    date = browser.cssselect('.article__head__meta__date')[0].text
    assert date.strip() == '3. November 2013'


def test_print_article_has_no_last_changed_date(testserver, testbrowser):
    # print articles should omit the last semantic change date
    article = testbrowser('%s/artikel/01' % testserver.url).contents
    assert '26. September 2013<span>editiert' not in article


def test_online_article_has_last_changed_date(selenium_driver, testserver):
    # online articles should include the last semantic change date
    driver = selenium_driver
    driver.get('%s/artikel/10' % testserver.url)
    meta_date = driver.find_element_by_class_name("article__head__meta__date")
    assert 'ZULETZT AKTUALISIERT AM 20. FEBRUAR 2014, '\
        '17:59 UHR' in meta_date.text


def test_product_page_has_last_changed_date(selenium_driver, testserver):
    # product pages should include the last semantic change date
    driver = selenium_driver
    driver.get('%s/produkte/katzen-cafe-london' % testserver.url)
    meta_date = driver.find_element_by_class_name("article__head__meta__date")
    assert 'ZULETZT AKTUALISIERT AM 31. JULI 2014, 22:21 UHR' in meta_date.text


def test_gallery_has_last_changed_date(selenium_driver, testserver):
    # galleries should include the last semantic change date
    driver = selenium_driver
    driver.get('%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    meta_date = driver.find_element_by_class_name("article__head__meta__date")
    assert 'ZULETZT AKTUALISIERT AM 3. APRIL 2014, 16:17 UHR' in meta_date.text


def test_article03_has_no_source(testserver, testbrowser):
    # zon source
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert 'article__head__meta__source' not in browser.contents


def test_article10_has_correct_online_source(testserver, testbrowser):
    # online source
    browser = testbrowser('%s/artikel/10' % testserver.url)
    meta_source = browser.cssselect('span.article__head__meta__source')[0]
    assert 'Erschienen bei golem.de' in meta_source.text_content()


def test_article08_has_correct_print_source(testserver, testbrowser):
    # print source
    browser = testbrowser('%s/artikel/08' % testserver.url)
    meta_source = browser.cssselect('span.article__head__meta__source')[0]
    assert u'DIE ZEIT Nr. 26/2008' in meta_source.text_content()


def test_article_1_10_produce_no_error(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/06' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/08' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/09' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/10' % testserver.url)
    assert browser.cssselect('div.article__wrap')


def test_article_1_10_have_correct_h1(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    browser = testbrowser('%s/artikel/06' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    browser = testbrowser('%s/artikel/08' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/09' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/10' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')


def test_header_articles_produce_no_error(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header3' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header4' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header5' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header5-2' % testserver.url)
    assert browser.cssselect('div.article__wrap')
    browser = testbrowser('%s/artikel/header6' % testserver.url)
    assert browser.cssselect('div.article__wrap')


def test_header_articles_have_correct_h1(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/header3' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/header4' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    browser = testbrowser('%s/artikel/header5' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')
    browser = testbrowser('%s/artikel/header6' % testserver.url)
    assert browser.cssselect('h1>div.article__head__title')
    assert browser.cssselect('h1>div.article__head__supertitle')


def test_article_header2_has_correct_subtitle(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert 'Wie viele Flüchtlingskinder bin '\
        'ich eine Suchende, Getriebene.' in browser.contents


def test_artikel_header_header1_should_have_correct_header_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    assert browser.cssselect('h1>.article__head__title')


def test_artikel_header_header2_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header2' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--traum')


def test_artikel_header_header3_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header3' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--text-only')


def test_artikel_header_header4_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header4' % testserver.url)
    assert browser.cssselect(
        'header.article__head.article__head--stamp.is-constrained')


def test_artikel_header_header5_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header5' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--leinwand')


def test_artikel_header_header6_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/header6' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--mode')


def test_artikel_header_standardkolumne_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--column')


def test_artikel_header_sequelpage_should_have_correct_source(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)
    assert browser.cssselect('header.article__head.article__head--sequel')


def test_nextread_teaser_block_has_teasers_available(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert hasattr(nextread, '__iter__'), 'Nextread block should be iterable.'
    assert len(nextread) == 1, '"Artikel 09" has exactly one nextread.'

    def func(a):
        return isinstance(a, zeit.content.article.article.Article)

    assert all(map(func, nextread)), 'All nextread teasers should be articles.'


def test_nextread_teaser_blocks_has_correct_layout_id(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 09" has a base nextread layout.'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'maximal', \
        '"Artikel 03" has a maximal nextread layout.'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/01')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 01" has no nextread layout, should fallback to base.'


def test_nextread_teaser_block_teasers_is_accessable(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert all(teaser for teaser in nextread), \
        'Nextread block should iterate over its teasers.'
    assert nextread[0], \
        'Nextread block should expose its teasers via index.'


def test_nextread_base_layout_has_image_element_if_available(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/09' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert len(nextread.cssselect('img')) == 1, \
        'There should be exactly one image tag in a "base" nextread teaser.'
    browser = testbrowser('%s/artikel/10' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert len(nextread.cssselect('img')) == 1, \
        'The nextread of "Artikel 10" has no teaser image asset.'


def test_nextread_maximal_layout_has_image_background_if_available(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/08' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert 'background-image' in nextread.attrib.get('style'), \
        'The teaser image should be set as a background for "maximal" teasers.'
    browser = testbrowser('%s/artikel/03' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert 'background-image' in nextread.attrib.get('style'), \
        'The nextread of "Artikel 03" has no teaser image asset.'


def test_nextread_should_fallback_to_default_layout(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 02" has invalid nextread layout, should fallback to base.'


def test_article_with_images_should_render_image_container(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert browser.cssselect('div.article__body > figure.figure-stamp')


def test_article_without_images_should_not_render_image_container(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/artikel-ohne-assets' % testserver.url)
    assert not browser.cssselect('div.article__page figure.figure-stamp')


def test_article_with_fictitious_imgs_should_not_render_img_contnr(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/artikel-mit-fiktiven-assets' % testserver.url)
    assert not browser.cssselect('div.article__page figure.figure-stamp')


def test_article03_has_linked_image(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    output = ""
    for line in browser.contents.splitlines():
        output += line.strip()
    assert '<a href="http://www.test.de"><img alt="Immer' in output


@pytest.mark.skipif(True,
                    reason="We need a way to mock liveblog in tests")
def test_article02_uses_esi(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/02' % testserver.url)
    blog = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "livedesk-root")))
    assert blog.is_displayed(), 'ESI Liveblog not displayed'


def test_article02_should_have_esi_include(testbrowser, testserver):
    browser = testbrowser('%s/artikel/02' % testserver.url)
    assert len(browser.cssselect('include')) == 1


def test_article_has_linked_copyright(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    output = ""
    for line in browser.contents.splitlines():
        output += line.strip()
    assert '<span class="figure__copyright">' \
        '<a href="http://foo.de" target="_blank">' \
        '© Reuters/Alessandro Bianchi' in output


def test_longform_has_linked_copyright(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    output = ""
    for line in browser.contents.splitlines():
        output += line.strip()
    assert '<span class="figure__copyright">' \
        '<a href="http://foo.de" target="_blank">' \
        '© Johannes Eisele/AFP/Getty Images' in output


def test_header_has_linked_copyright(testserver, testbrowser):
    browser = testbrowser('%s/artikel/header1' % testserver.url)
    output = ""
    for line in browser.contents.splitlines():
        output += line.strip()
    assert '<span class="figure__copyright">' \
        '<a href="http://foo.de" target="_blank">©foo' in output


def test_feature_longform_should_have_zon_logo_classes(
        testserver, testbrowser):
    browser = testbrowser('%s/feature/feature_longform' % testserver.url)
    assert browser.cssselect('.main-nav__logo__img.icon-logo-zon-small')
    logolink = browser.cssselect('a.main-nav__logo')
    assert logolink[0].attrib['href'] == '{}/index'.format(
        testserver.url)


def test_feature_longform_should_have_zonish_title(testserver, testbrowser):

    browser = testbrowser('%s/feature/feature_longform' % testserver.url)
    title = browser.cssselect('head > title')
    assert 'ZEIT ONLINE' in title[0].text


def test_feature_longform_should_have_zon_twittername(testserver, testbrowser):

    browser = testbrowser('%s/feature/feature_longform' % testserver.url)
    creator = browser.cssselect('meta[name="twitter:site"]')
    assert creator[0].values()[1] == '@zeitonline'


def test_article_view_has_leadtime_set_if_article_provides_it(
        testserver, testbrowser):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    assert view.leadtime.start
    assert view.leadtime.end


def test_article_view_has_no_leadtime_if_the_attribute_is_missing(
        testserver, testbrowser):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    assert view.leadtime.start is None
    assert view.leadtime.end is None


def test_advertorial_article_shows_advertorial_marker(testserver, testbrowser):
    browser = testbrowser('%s/artikel/advertorial' % testserver.url)
    assert browser.cssselect(
        '.advertorial-navigation-title')[0].text == 'Anzeige'
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert not browser.cssselect('.advertorial-navigation-title')


def test_articles_should_have_exact_one_h1(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/02' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/03' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/04' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/05' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/07' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/08' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/09' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/10' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header1' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header2' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header3' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header4' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header5' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1

    browser = testbrowser('%s/artikel/header6' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1


def test_longform_should_have_exact_one_h1(testserver, testbrowser):
    browser = testbrowser('%s/artikel/06' % testserver.url)
    h1s = browser.cssselect('h1')
    assert len(h1s) == 1


def test_article_first_page_must_have_no_image_as_first_block(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(
        context).values()[0]
    block = zeit.web.core.article.pages_of_article(context)[0][0]

    assert zeit.content.article.edit.interfaces.IImage.providedBy(
        body), ('Image should be present on first position in \
        article body.')
    assert not zeit.content.article.edit.interfaces.IImage.providedBy(
        block), 'Image must not be present on first position in page.'


def test_zmo_should_not_render_advertisement_nextread(
        testbrowser, workingcopy):
    # /artikel/10 has ressort 'Wirtschaft' which has ad-nextread content.
    browser = testbrowser('/artikel/10')
    assert len(browser.cssselect('.nextread-advertisement')) == 0


def test_article_contains_zeit_clickcounter(testbrowser):
    browser = testbrowser('/artikel/03')
    counter = browser.cssselect('body noscript img[src^="http://cc.zeit.de"]')
    assert ("img.src = 'http://cc.zeit.de/cc.gif?banner-channel="
            "zeitmz/essenundtrinken/article") in browser.contents
    assert len(counter) == 1
    assert ('cc.zeit.de/cc.gif?banner-channel=zeitmz/essenundtrinken/article'
        ) in counter[0].get('src')
