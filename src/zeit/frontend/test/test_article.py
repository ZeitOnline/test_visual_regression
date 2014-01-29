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


def test_article_sharing_meta_html(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/03' % testserver.url)
    for meta in driver.find_elements_by_tag_name('meta'):
        #twitter
        if meta.get_attribute("name") == 'twitter:card':
            assert 'summary' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:site':
            assert '@zeitonline' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:creator':
            assert '@zeitonline' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:title':
            assert 'Der Chianti hat eine zweite Chance verdient' == \
                unicode(meta.get_attribute("content"))
        if meta.get_attribute("name") == 'twitter:description':
            assert 'Erst Heilsbringer, dann Massenware: ' \
                'Der Chianti ist tief gefallen. Doch engagierte ' \
                'Winzer retten dem Wein in der Bastflasche die Ehre. ' == \
                unicode(meta.get_attribute("content"))
        #fb
        if meta.get_attribute("property") == 'og:site_name':
            assert 'ZEIT ONLINE' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'fb:admins':
            assert '595098294' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'og:type':
            assert 'article' == unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'og:title':
            assert 'Der Chianti hat eine zweite Chance verdient' == \
                unicode(meta.get_attribute("content"))
        if meta.get_attribute("property") == 'og:description':
            assert 'Erst Heilsbringer, dann Massenware: ' \
                'Der Chianti ist tief gefallen. Doch engagierte ' \
                'Winzer retten dem Wein in der Bastflasche die Ehre. ' == \
                unicode(meta.get_attribute("content"))
        #images
        if meta.get_attribute("property") == 'og:image':
            assert 'scaled-image' == unicode(meta.get_attribute("class"))
        if meta.get_attribute("name") == 'twitter:image':
            assert 'scaled-image' == unicode(meta.get_attribute("class"))
