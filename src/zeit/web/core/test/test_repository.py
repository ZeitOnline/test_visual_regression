import zeit.content.article.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.unknown


def test_content_should_have_marker_interface(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    assert zeit.web.core.interfaces.IInternalUse.providedBy(content)


def test_dynamic_content_should_have_marker_interface(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/angela-merkel')
    assert zeit.web.core.interfaces.IInternalUse.providedBy(content)


def test_content_without_type_should_have_no_content_interfaces(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/missing-contenttype')
    assert isinstance(
        content, zeit.cms.repository.unknown.PersistentUnknownResource)
    assert not zeit.content.article.interfaces.IArticle.providedBy(content)
