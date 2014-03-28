import zope.testbrowser.wsgi


def test_renders_image(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'http://www.zeit.de/artikel/01' in b.contents
    assert 'http://www.zeit.de/artikel/02' in b.contents
    assert ('http://images.zeit.de/exampleimages/artikel/01'
            '/group/group-148x84.jpg' in b.contents)
