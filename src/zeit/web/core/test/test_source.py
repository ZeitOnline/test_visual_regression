import zope.app.appsetup.product

import zeit.cms.content.sources


class DummySource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web.test'
    config_url = 'dummy-source'


def test_source_returns_empty_list_when_file_is_unreadable(application):
    zope.app.appsetup.product.setProductConfiguration('zeit.web.test', {})
    config = zope.app.appsetup.product.getProductConfiguration('zeit.web.test')
    config['dummy-source'] = 'file:///nonexistent'
    assert list(DummySource()) == []
