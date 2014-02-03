from StringIO import StringIO
from zeit.content.article.article import Article
from zeit.frontend.interfaces import IPages


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
    title = driver.find_element_by_class_name('article__title').text.strip()
    path = "//span[@class='article__subtitle']/p"
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
            assert unicode(desc) == \
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
    title = driver.find_element_by_class_name('article__title').text.strip()
    path = "//span[@class='article__subtitle']/p"
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
            assert unicode(desc) == \
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
