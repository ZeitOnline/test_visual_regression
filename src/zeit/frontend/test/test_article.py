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
