# -*- coding: utf-8 -*-
from StringIO import StringIO
import mock

from zeit.content.article.article import Article
import zeit.cms.interfaces

from zeit.web.core.interfaces import IPages
import zeit.web.magazin.view_article


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


def test_article_has_valid_twitter_meta_tags(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert (
        '<meta name="twitter:card" content="summary_large_image">'
        in browser.contents)
    assert '<meta name="twitter:site"'\
        ' content="@zeitonline">' in browser.contents
    assert '<meta name="twitter:creator"'\
        ' content="@zeitonline">' in browser.contents
    assert '<meta name="twitter:title"'\
        ' content="Mei, is des traurig!">' in browser.contents
    assert '<meta name="twitter:description"'\
        ' content="Die Münchner Schoppenstube hat dichtgemacht.'\
        ' Was erzählt uns das über die Gentrifizierung?'\
        ' Ein Erklärungsversuch.">' in browser.contents
    assert '<meta name="twitter:image:src"' in browser.contents


def test_article_has_valid_facebook_meta_tags(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    assert '<meta property="og:site_name" '\
        'content="ZEIT ONLINE">' in browser.contents
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


def test_article03_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)
    assert '1: "Anne Mustermann",' in browser.contents
    assert '2: "zeitmz/essenundtrinken/article",' in browser.contents
    assert '3: "2/7",' in browser.contents
    assert '4: "Wein;Italien;Toskana;Bologna;Bozen;Florenz;Tübingen",' \
        in browser.contents
    assert '6: "4952",' in browser.contents
    assert '7: "",' in browser.contents
    assert '9: "zeitmz/essenundtrinken/article"' in browser.contents
    assert '1: "Redaktion",' in browser.contents
    assert '2: "Artikel",' in browser.contents
    assert '3: "lebensart",' in browser.contents
    assert '4: "Online"' in browser.contents

    assert '5: "essen-trinken",' in browser.contents
    assert '6: "weinkolumne",' in browser.contents
    assert '7: "seite-2",' in browser.contents
    assert '8: "zeitmz/essenundtrinken/article",' in \
        browser.contents
    assert '9: "2013-07-30"' in browser.contents
    assert 'http://zeit01.webtrekk.net/981949533494636/' \
        'wt.pl?p=311,redaktion.lebensart.essen-trinken..' \
        'article.online./artikel/03/seite-2,0,0,0,0,0,0,0,0' \
        '&amp;cg1=Redaktion&amp;cg2=Artikel&amp;cg3=lebensart' \
        '&amp;cg4=Online&amp;cg5=essen-trinken&amp;cg6=&amp;' \
        'cg7=seite-2&amp;cg8=zeitmz/essenundtrinken/article' \
        '&amp;cg9=2013-07-30&amp;cp1=Anne Mustermann&amp;' \
        'cp2=zeitmz/essenundtrinken/article&amp;cp3=2/7' \
        '&amp;cp4=Wein;Italien;Toskana;Bologna;Bozen;Florenz;' \
        'Tübingen&amp;cp6=4952&amp;cp7=&amp;' \
        'cp9=zeitmz/essenundtrinken/article' in browser.contents


def test_article08_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser('%s/artikel/08' % testserver.url)
    assert '1: "Anne Mustermann;Oliver Fritsch",' in browser.contents
    assert '2: "politik/article",' in browser.contents
    assert '3: "1/1",' in browser.contents
    assert '4: "Politik",' in browser.contents
    assert '6: "2833",' in browser.contents
    assert '7: "",' in browser.contents
    assert '9: "politik/article"' in browser.contents
    assert '1: "Redaktion",' in browser.contents
    assert '2: "Artikel",' in browser.contents
    assert '3: "politik",' in browser.contents
    assert '4: "Online"' in browser.contents
    assert '5: "",' in browser.contents
    assert '6: "",' in browser.contents
    assert '7: "08",' in browser.contents
    assert '8: "politik/article",' in browser.contents
    assert '9: "2014-02-19"' in browser.contents
    assert 'http://zeit01.webtrekk.net/981949533494636/' \
        'wt.pl?p=311,redaktion.politik...article.online./' \
        'artikel/08,0,0,0,0,0,0,0,0&amp;cg1=Redaktion&amp;' \
        'cg2=Artikel&amp;cg3=politik&amp;cg4=Online&amp;' \
        'cg5=&amp;cg6=&amp;cg7=08&amp;cg8=politik/article&amp;' \
        'cg9=2014-02-19&amp;cp1=Anne Mustermann;Oliver Fritsch&amp;' \
        'cp2=politik/article&amp;cp3=1/1&amp;cp4=Politik&amp;' \
        'cp6=2833&amp;cp7=&amp;cp9=politik/article' in browser.contents


def test_cp_has_correct_webtrekk_values(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert '1: "Redaktion",' in browser.contents
    assert '2: "Centerpage",' in browser.contents
    assert '3: "lebensart",' in browser.contents
    assert '4: "Online",' in browser.contents
    assert '5: "",' in browser.contents
    assert '6: "",' in browser.contents
    assert '7: "test-cp-zmo",' in browser.contents
    assert '8: "zeitmz/centerpage",' in browser.contents
    assert '9: ""' in browser.contents
    assert 'wt.pl?p=311,redaktion.lebensart...' \
        'centerpage.online./zeit-magazin/test-cp/test-cp-zmo,' \
        '0,0,0,0,0,0,0,0&amp;cg1=Redaktion&amp;cg2=Centerpage&amp;' \
        'cg3=lebensart&amp;cg4=Online&amp;cg5=&amp;cg6=&amp;' \
        'cg7=test-cp-zmo&amp;' \
        'cg8=zeitmz/centerpage&amp;cg9=' in browser.contents


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
        ' zweite Chance verdient' in browser.contents


def test_article_should_have_correct_seo_title(testserver, testbrowser):
    browser = testbrowser('%s/artikel/04' % testserver.url)
    assert '<title>SEO title</title>' in browser.contents


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


def test_article08_has_correct_date(testserver, testbrowser):
    # not updated print article
    browser = testbrowser('%s/artikel/08' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '19. Februar 2014</span>' in browser.contents


def test_article09_has_correct_date(testserver, testbrowser):
    # updated print article
    browser = testbrowser('%s/artikel/09' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '4. März 2014, 14:35 Uhr</span>' in browser.contents


def test_article03_has_correct_date(testserver, testbrowser):
    # not updated online article
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '30. Juli 2013, 17:20 Uhr</span>' in browser.contents


def test_article10_has_correct_date(testserver, testbrowser):
    # updated online article
    browser = testbrowser('%s/artikel/10' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '20. Februar 2014, 17:59 Uhr</span>' in browser.contents


def test_article05_has_correct_date(testserver, testbrowser):
    # longform
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert '<span class="article__head__meta__date">'\
        '3. November 2013</span>' in browser.contents


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
    assert '<span class="article__head__meta__source">'\
        'golem.de</span>' in browser.contents


def test_article08_has_correct_print_source(testserver, testbrowser):
    # print source
    browser = testbrowser('%s/artikel/08' % testserver.url)
    meta_source = browser.cssselect('span.article__head__meta__source')[0]
    assert 'DIE ZEIT Nr. 26/2008' in meta_source.text_content()


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


def test_gallery_should_have_clickCounter_functions(testserver, testbrowser):
    browser = testbrowser(
        '%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    assert 'var clickCount = {' in browser.contents


def test_nextread_teaser_block_has_teasers_available(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
    assert isinstance(nextread.teasers, tuple), \
        'The "teasers" attribute should return a tuple.'
    assert len(nextread.teasers) == 1, \
        '"Artikel 09" has exactly one nextread.'
    assert all(map(lambda a: isinstance(a, Article), nextread.teasers)), \
        'All nextread teasers should be articles.'


def test_nextread_teaser_blocks_has_correct_layout_id(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 09" has a base nextread layout.'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
    assert nextread.layout.id == 'maximal', \
        '"Artikel 03" has a maximal nextread layout.'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/01')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 01" has no nextread layout, should fallback to base.'


def test_nextread_teaser_block_teasers_is_accessable(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
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
    assert len(nextread.cssselect('img')) == 0, \
        'The nextread of "Artikel 10" has no teaser image asset.'


def test_nextread_maximal_layout_has_image_background_if_available(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/08' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert 'background-image' in nextread.attrib.get('style'), \
        'The teaser image should be set as a background for "maximal" teasers.'
    browser = testbrowser('%s/artikel/03' % testserver.url)
    nextread = browser.cssselect('div.article__nextread__body')[0]
    assert 'background-image' not in nextread.attrib.get('style'), \
        'The nextread of "Artikel 03" has no teaser image asset.'


def test_nextread_should_fallback_to_default_layout(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    nextread = zeit.web.core.interfaces.INextreadTeaserBlock(context)
    assert nextread.layout.id == 'base', \
        '"Artikel 02" has invalid nextread layout, should fallback to base.'


def test_article_with_images_should_render_image_container(
        testserver, testbrowser):
    browser = testbrowser('%s/artikel/03' % testserver.url)
    assert browser.cssselect('div.article__page figure.figure-stamp')


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


def test_article02_uses_esi(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/02' % testserver.url)
    blog = driver.find_elements_by_id("livedesk-root")
    assert len(blog) != 0


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
    assert logolink[0].attrib['href'] == "http://www.zeit.de/index"


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
