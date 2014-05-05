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


def test_article_has_valid_twitter_meta_tags(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    title = driver.find_element_by_class_name('article__head__title').text.strip()
    path = "//div[@class='article__head__subtitle']/p"
    desc = driver.find_element_by_xpath(path).text.strip()

    for meta in driver.find_elements_by_tag_name('meta'):
        if meta.get_attribute("name") == 'twitter:card':
            assert 'summary' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:site':
            assert '@zeitonline' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:creator':
            assert '@zeitonline' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:title':
            assert unicode(title) == \
                unicode(meta.get_attribute("content").strip())
        if meta.get_attribute("name") == 'twitter:description':
            assert unicode(desc.strip(' Von Anne Mustermann')) == \
                unicode(meta.get_attribute("content").strip())
        if meta.get_attribute("name") == 'twitter:image':
            assert 'scaled-image' == unicode(meta.get_attribute("class"))


def test_article_has_all_twitter_meta_tags(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    driver.find_element_by_xpath("//meta[@name='twitter:card']")
    driver.find_element_by_xpath("//meta[@name='twitter:site']")
    driver.find_element_by_xpath("//meta[@name='twitter:creator']")
    driver.find_element_by_xpath("//meta[@name='twitter:title']")
    driver.find_element_by_xpath("//meta[@name='twitter:description']")


def test_article_has_valid_facebook_meta_tags(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    title = driver.find_element_by_class_name('article__head__title').text.strip()
    path = "//div[@class='article__head__subtitle']/p"
    desc = driver.find_element_by_xpath(path).text.strip()

    for meta in driver.find_elements_by_tag_name('meta'):
        if meta.get_attribute("property") == 'og:site_name':
            assert 'ZEIT ONLINE' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'fb:admins':
            assert '595098294' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'og:type':
            assert 'article' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'og:title':
            assert unicode(title) == \
                unicode(meta.get_attribute("content").strip())
        if meta.get_attribute("property") == 'og:description':
            assert unicode(desc.strip(' Von Anne Mustermann')) == \
                unicode(meta.get_attribute("content").strip())
        if meta.get_attribute("property") == 'og:image':
            assert 'scaled-image' == unicode(meta.get_attribute("class"))


def test_article_has_all_facebook_meta_tags(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    driver.find_element_by_xpath("//meta[@property='og:site_name']")
    driver.find_element_by_xpath("//meta[@property='fb:admins']")
    driver.find_element_by_xpath("//meta[@property='og:type']")
    driver.find_element_by_xpath("//meta[@property='og:title']")
    driver.find_element_by_xpath("//meta[@property='og:description']")


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


def test_article_has_correct_page_title(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    title = driver.title.strip()
    assert title == 'Kolumne Die Ausleser: Der Chianti hat eine zweite Chance verdient'


def test_article_without_supertitle_has_correct_page_title(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03a' % testserver.url)
    title = driver.title.strip()
    assert title == 'Der Chianti hat eine zweite Chance verdient'


def test_article_has_correct_page_meta_description(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="description"]')
    teststring = 'Erst Heilsbringer, dann Massenware: Der Chianti ist tief gefallen. ' \
                 'Doch engagierte Winzer retten dem Wein in der Bastflasche die Ehre.'
    assert meta_description_tag.get_attribute("content").strip() == teststring


def test_article_has_correct_page_meta_keywords(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="keywords"]')
    teststring = u'Wein, Italien, Toskana, Bologna, Bozen, Florenz, T\xfcbingen'
    assert meta_description_tag.get_attribute("content").strip() == teststring


def test_article08_has_correct_date(selenium_driver, testserver):
    # not updated print article
    driver = selenium_driver
    driver.get('%s/artikel/08' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__date')\
        .text.strip()
    assert text == '19. FEBRUAR 2014'


def test_article09_has_correct_date(selenium_driver, testserver):
    # updated print article
    driver = selenium_driver
    driver.get('%s/artikel/09' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__date')\
        .text.strip()
    assert text == u'04. M\xc4RZ 2014, 14:35 UHR'


def test_article03_has_correct_date(selenium_driver, testserver):
    # not updated online article
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__date')\
        .text.strip()
    assert text == u'30. JULI 2013, 17:20 UHR'


def test_article10_has_correct_date(selenium_driver, testserver):
    # updated online article
    driver = selenium_driver
    driver.get('%s/artikel/10' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__date')\
        .text.strip()
    assert text == u'20. FEBRUAR 2014, 17:59 UHR'


def test_article05_has_correct_date(selenium_driver, testserver):
    # longform
    driver = selenium_driver
    driver.get('%s/artikel/05' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__date')\
        .text.strip()
    assert text == u'03. NOVEMBER 2013'


def test_print_article_has_no_last_changed_date(testserver):
    # print articles should omit the last semantic change date
    article = Browser('%s/artikel/01' % testserver.url).contents
    assert '26. September 2013<span>editiert' not in article


def test_online_article_has_last_changed_date(testserver):
    # online articles should include the last semantic change date
    article = Browser('%s/artikel/04' % testserver.url).contents
    assert '01. Oktober 2013, 16:38 Uhr<span>editiert' in article


def test_article03_has_no_source(selenium_driver, testserver):
    # zon source
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    class_name = '.article__head__meta__source'
    assert len(driver.find_elements_by_css_selector(class_name)) == 0


def test_article10_has_correct_online_source(selenium_driver, testserver):
    # online source
    driver = selenium_driver
    driver.get('%s/artikel/10' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__source')\
        .text.strip()
    assert text == 'GOLEM.DE'


def test_article08_has_correct_print_source(selenium_driver, testserver):
    # print source
    driver = selenium_driver
    driver.get('%s/artikel/08' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta__source')\
        .text.strip()
    assert text == 'DIE ZEIT NR. 26/2008'


def test_article08_has_correct_author_text(selenium_driver, testserver):
    # print source
    driver = selenium_driver
    driver.get('%s/artikel/08' % testserver.url)
    text = driver.find_element_by_class_name('article__head__meta')\
        .text.strip()
    assert text == 'DIE ZEIT NR. 26/2008 19. FEBRUAR 2014'


def test_article_1_10_produces_no_error(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/02' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/03' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/04' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/05' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/06' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/07' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/08' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/09' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/artikel/10' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0


def test_article_header2_has_correct_subtitle(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/header2' % testserver.url)
    text = driver.find_element_by_class_name('article__head__subtitle')\
        .text.strip()
    assert text == u'\u00BBWie viele Fl\u00FCchtlingskinder bin '\
        u'ich eine Suchende, Getriebene.\u00AB'


def test_artikel_header_header1_should_have_correct_header_source(testserver):
    browser = Browser('%s/artikel/header1' % testserver.url)
    assert '<h1 class="article__head__title">' in browser.contents


def test_artikel_header_header2_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert '<header class="article__head article__head--traum">' in browser.contents


def test_artikel_header_header3_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header3' % testserver.url)
    assert '<header class="article__head article__head--text-only">' in browser.contents


def test_artikel_header_header4_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header4' % testserver.url)
    assert '<header class="article__head article__head--stamp is-constrained">' in browser.contents


def test_artikel_header_header5_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header5' % testserver.url)
    assert '<header class="article__head article__head--leinwand">' in browser.contents


def test_artikel_header_header6_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/header6' % testserver.url)
    assert '<header class="article__head article__head--mode">' in browser.contents


def test_artikel_header_standardkolumne_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert '<header class="article__head article__head--column">' in browser.contents


def test_artikel_header_sequelpage_should_have_correct_source(testserver):
    browser = Browser('%s/artikel/03/seite-2' % testserver.url)
    assert '<header class="article__head article__head--sequel">' in browser.contents
