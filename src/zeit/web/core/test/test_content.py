import lxml.objectify

import zeit.cms.content.interfaces

import zeit.web.core.content


def test_exposing_proxy_should_return_dummy_for_unresolveable_uniqueId(
        application):
    proxy = zeit.web.core.content.LazyProxy({
        'uniqueId': 'http://xml.zeit.de/nonexistent', 'type': 'article'})
    assert proxy.ressort is None
    # assert nothing raised:
    zeit.cms.content.interfaces.IXMLReferenceUpdater(proxy).update(
        lxml.objectify.XML('<foo/>'))


def test_proxy_should_compare_to_CMSContent(application):
    # Without this, IArea.hide_dupes does not work (BUG-931)
    art = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    p1 = zeit.web.core.content.LazyProxy({
        'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
        'type': 'article'})
    p2 = zeit.web.core.content.LazyProxy({
        'uniqueId': 'http://xml.zeit.de/zeit-online/article/01',
        'type': 'article'})
    assert p1 == p2
    assert p1 == art
