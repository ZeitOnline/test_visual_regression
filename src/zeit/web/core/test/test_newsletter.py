import mock
import zope.testbrowser.wsgi

import zeit.cms.interfaces
import zeit.newsletter.interfaces


def test_renders_image(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'http://www.zeit.de/zeit-magazin/article/01' in b.contents
    assert 'http://www.zeit.de/zeit-magazin/article/02' in b.contents
    assert ('http://www.zeit.de/exampleimages/artikel/01'
            '/schoppenstube/wide__148x84' in b.contents)


def test_renders_videos(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar')
    assert 'http://www.zeit.de/zeit-magazin/article/01' in b.contents
    assert 'Skispringen' in b.contents


def test_plaintext_format_has_proper_contenttype(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    b.open('http://localhost/newsletter/februar?format=txt')
    assert 'text/plain; charset=utf-8' == b.headers['Content-Type']


def test_can_access_category(application):
    newsletter = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/newsletter/februar')
    category = zeit.newsletter.interfaces.INewsletterCategory(newsletter)
    assert category.subject == 'ZEIT ONLINE Newsletter'


def test_newsletter_does_not_render_image_if_expired(application):
    b = zope.testbrowser.wsgi.Browser(wsgi_app=application)
    with mock.patch(
            'zeit.web.core.image.ImageExpiration.is_expired') as expired:
        expired.return_value = True
        b.open('http://localhost/newsletter/februar')
    assert ('http://www.zeit.de/exampleimages/artikel/01/schoppenstube'
            not in b.contents)
