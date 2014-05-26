# -*- coding: utf-8 -*-
from StringIO import StringIO
from zeit.content.article.article import Article
from zeit.frontend.interfaces import IPages
from zope.testbrowser.browser import Browser


def test_IPages_contains_blocks(application):
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
    article = Article(xml)
    pages = IPages(article)
    assert 2 == len(pages)
    assert 'foo bar\n' == str(list(pages[0])[0])
    assert 1 == pages[1].number
    assert 'Zweite' == pages[1].teaser


def test_article_has_valid_twitter_meta_tags(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<meta name="twitter:card" content="summary">' in browser.contents
    assert '<meta name="twitter:site"'\
        ' content="@zeitonline">' in browser.contents
    assert '<meta name="twitter:creator"'\
        ' content="@zeitonline">' in browser.contents
    assert '<meta name="twitter:title"'\
        ' content="Der Chianti hat eine'\
        ' zweite Chance verdient">' in browser.contents
    assert '<meta name="twitter:description"'\
        ' content="Erst Heilsbringer, dann Massenware:'\
        ' Der Chianti ist tief gefallen. Doch engagierte Winzer'\
        ' retten dem Wein in der Bastflasche die Ehre. ">' in browser.contents
    assert '<meta class="scaled-image"'\
        ' name="twitter:image"' in browser.contents


def test_article_has_valid_facebook_meta_tags(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<meta property="og:site_name" '\
        'content="ZEIT ONLINE">' in browser.contents
    assert '<meta property="fb:admins"'\
        ' content="595098294">' in browser.contents
    assert '<meta property="og:type"'\
        ' content="article">' in browser.contents
    assert '<meta property="og:title"'\
        ' content="Der Chianti hat eine'\
        ' zweite Chance verdient">' in browser.contents
    assert '<meta property="og:description"'\
        ' content="Erst Heilsbringer, dann Massenware:'\
        ' Der Chianti ist tief gefallen. Doch engagierte Winzer'\
        ' retten dem Wein in der Bastflasche die Ehre. ">' in browser.contents
    assert '<meta property="og:image" class="scaled-image"' in browser.contents


def test_all_tracking_pixel_are_send(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/05' % testserver.url)
    driver.find_element_by_xpath(
        "//script[@src='http://www.google-analytics.com/ga.js']")
    driver.find_element_by_xpath(
        "//script[@src='http://scripts.zeit.de/js/rsa.js']")
    driver.find_element_by_xpath(
        "//script[@src='http://scripts.zeit.de/static/js/" +
        "webtrekk/webtrekk_v3.js']")
    driver.find_element_by_xpath(
        "//script[@src='https://script.ioam.de/iam.js']")
    driver.find_element_by_xpath(
        "//img[starts-with(@src,'http://cc.zeit.de/cc.gif')]")
    driver.find_element_by_xpath(
        "//img[starts-with(@src,'http://zeitonl.ivwbox.de')]")


def test_ivw_tracking_for_mobile_and_desktop(selenium_driver, testserver):
    driver = selenium_driver
    # ipad landscape
    driver.set_window_size(1024, 768)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "zeitonl"
    # ipad portrait and smaller
    driver.set_window_size(766, 1024)
    driver.get('%s/artikel/01' % testserver.url)
    content = driver.execute_script("return iam_data.st")
    assert content == "mobzeit"


def test_article_has_correct_page_title(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<title>Kolumne Die Ausleser:'\
        ' Der Chianti hat eine'\
        ' zweite Chance verdient' in browser.contents


def test_article_without_supertitle_has_correct_page_title(testserver):
    browser = Browser('%s/artikel/03a' % testserver.url)
    assert '<title>'\
        'Der Chianti hat eine'\
        ' zweite Chance verdient' in browser.contents


def test_article_should_have_correct_seo_title(testserver):
    browser = Browser('%s/artikel/04' % testserver.url)
    assert '<title>SEO title</title>' in browser.contents


def test_article_has_correct_page_meta_description(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<meta name="description" '\
        'content="Erst Heilsbringer, dann Massenware:'\
        ' Der Chianti ist tief gefallen. Doch'\
        ' engagierte Winzer retten dem Wein in der'\
        ' Bastflasche die Ehre. ">' in browser.contents


def test_article_should_have_correct_seo_description(testserver):
    browser = Browser('%s/artikel/04' % testserver.url)
    assert '<meta name="description" content="SEO description">' \
        in browser.contents


def test_article_has_correct_page_meta_keywords(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<meta name="keywords" content="Wein, Italien,'\
        ' Toskana, Bologna, Bozen, Florenz, Tübingen">' in browser.contents


def test_article08_has_correct_date(testserver):
    # not updated print article
    browser = Browser('%s/artikel/08' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '19. Februar 2014</span>' in browser.contents


def test_article09_has_correct_date(testserver):
    # updated print article
    browser = Browser('%s/artikel/09' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '4. März 2014, 14:35 Uhr</span>' in browser.contents


def test_article03_has_correct_date(testserver):
    # not updated online article
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '30. Juli 2013, 17:20 Uhr</span>' in browser.contents


def test_article10_has_correct_date(testserver):
    # updated online article
    browser = Browser('%s/artikel/10' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '20. Februar 2014, 17:59 Uhr</span>' in browser.contents


def test_article05_has_correct_date(testserver):
    # longform
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '3. November 2013</span>' in browser.contents


def test_print_article_has_no_last_changed_date(testserver):
    # print articles should omit the last semantic change date
    article = Browser('%s/artikel/01' % testserver.url).contents
    assert '26. September 2013<span>editiert' not in article


def test_online_article_has_last_changed_date(testserver):
    # online articles should include the last semantic change date
    article = Browser('%s/artikel/04' % testserver.url).contents
    assert '1. Oktober 2013, 16:38 Uhr' in article


def test_article03_has_no_source(testserver):
    # zon source
    browser = Browser('%s/artikel/03' % testserver.url)
    assert 'article__head__meta__source' not in browser.contents


def test_article10_has_correct_online_source(testserver):
    # online source
    browser = Browser('%s/artikel/10' % testserver.url)
    assert '<span class="article__head__meta__source">'\
        'golem.de</span>' in browser.contents


def test_article08_has_correct_print_source(testserver):
    # print source
    browser = Browser('%s/artikel/08' % testserver.url)
    assert '<span class="article__head__meta__source">'\
        'DIE ZEIT Nr. 26/2008</span>' in browser.contents


def test_article_1_10_produce_no_error(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/02' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/03' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/04' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/06' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/07' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/08' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/09' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/10' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents


def test_header_articles_produce_no_error(testserver):
    browser = Browser('%s/artikel/header1' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/header3' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/header4' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/header5' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents
    browser = Browser('%s/artikel/header6' % testserver.url)
    assert '<div class="article__wrap">' in browser.contents


def test_article_header2_has_correct_subtitle(testserver):
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert 'Wie viele Flüchtlingskinder bin '\
        'ich eine Suchende, Getriebene.' in browser.contents


def test_artikel_header_header1_should_have_correct_header_source(testserver):
    browser = Browser('%s/artikel/header1' % testserver.url)
    assert '<h1 class="article__head__title">' in browser.contents


def test_artikel_header_header2_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert '<header class="article__head '\
        'article__head--traum">' in browser.contents


def test_artikel_header_header3_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header3' % testserver.url)
    assert '<header class="article__head '\
        'article__head--text-only">' in browser.contents


def test_artikel_header_header4_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header4' % testserver.url)
    assert '<header class="article__head '\
        'article__head--stamp is-constrained">' in browser.contents


def test_artikel_header_header5_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header5' % testserver.url)
    assert '<header class="article__head '\
        'article__head--leinwand">' in browser.contents


def test_artikel_header_header6_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header6' % testserver.url)
    assert '<header class="article__head '\
        'article__head--mode">' in browser.contents


def test_artikel_header_standardkolumne_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert '<header class="article__head '\
        'article__head--column">' in browser.contents


def test_artikel_header_sequelpage_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/03/seite-2' % testserver.url)
    assert '<header class="article__head '\
        'article__head--sequel">' in browser.contents
