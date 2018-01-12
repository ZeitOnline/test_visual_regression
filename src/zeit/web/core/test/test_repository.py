import mock
import pyramid.request

from zeit.cms.checkout.helper import checked_out
import zeit.content.article.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.unknown


def test_resolving_should_not_use_traversal(application):
    def get_and_record(self, uniqueId):
        calls.append(uniqueId)
        return original_get(self, uniqueId)
    original_get = zeit.connector.filesystem.Connector.__getitem__
    calls = []
    with mock.patch('zeit.connector.filesystem.Connector.__getitem__',
                    new=get_and_record):
        zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-online/article/01')
        assert 'http://xml.zeit.de/zeit-online/' not in calls
        assert 'http://xml.zeit.de/zeit-online/article/' not in calls


def test_traversal_should_not_resolve_parents(application):
    folder = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/')
    with mock.patch('zeit.content.article.article.Article.__parent__',
                    new=mock.PropertyMock()) as parent:
        folder['01']
        assert not parent.called


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


def test_workingcopy_content_should_have_marker_interface(
        my_traverser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/fischer')
    with checked_out(content, temporary=False):
        req = pyramid.request.Request.blank('/wcpreview/zope.user/fischer')
        tdict = my_traverser(req)
        assert zeit.web.core.interfaces.IInternalUse.providedBy(
            tdict['context'])
