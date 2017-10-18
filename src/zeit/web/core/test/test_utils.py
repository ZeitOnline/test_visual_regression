import lxml.objectify

import zeit.cms.content.interfaces

import zeit.web.core.utils


def test_exposing_proxy_should_return_dummy_for_unresolveable_uniqueId(
        application):
    proxy = zeit.web.core.utils.LazyProxy({
        'uniqueId': 'http://xml.zeit.de/nonexistent', 'type': 'article'})
    assert proxy.ressort is None
    # assert nothing raised:
    zeit.cms.content.interfaces.IXMLReferenceUpdater(proxy).update(
        lxml.objectify.XML('<foo/>'))
