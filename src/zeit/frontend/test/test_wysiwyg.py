from zeit.cms.interfaces import ICMSContent
from zeit.wysiwyg.interfaces import IHTMLContent


def test_accessing_html_body_works(application):
    gallery = ICMSContent(
        'http://xml.zeit.de/galerien/bg-automesse-detroit-2014-usa')
    assert '' == IHTMLContent(gallery).html
