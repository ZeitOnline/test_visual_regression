import pytest
import zope.testbrowser.wsgi


@pytest.mark.skipif(
    True, reason='XXX need to set up pseudo-DAV template loader')
def test_renders_image(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'href="http://www.zeit.de/artikel/01"' in b.contents
    assert 'href="http://www.zeit.de/artikel/02"' in b.contents
    assert ('src="http://images.zeit.de/exampleimages/artikel/01'
            '/group/group-148x84.jpg"/>' in b.contents)
