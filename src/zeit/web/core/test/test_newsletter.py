import zope.testbrowser.wsgi


def test_renders_image(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'http://www.zeit.de/artikel/01' in b.contents
    assert 'http://www.zeit.de/artikel/02' in b.contents
    assert ('http://images.zeit.de/exampleimages/artikel/01'
            '/schoppenstube/schoppenstube-148x84.jpg' in b.contents)


def test_renders_videos(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'http://www.zeit.de/artikel/01' in b.contents
    assert 'Skispringen' in b.contents


def test_plaintext_format_has_proper_contenttype(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar?format=txt')
    assert 'text/plain; charset=utf-8' == b.headers['Content-Type']
