import pytest

import zeit.content.cp.interfaces

import zeit.web.site.module.headerimage
import zeit.web.core.utils


@pytest.fixture
def headerimage(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index-with-image')
    block = zeit.web.core.utils.find_block(
        context, module='headerimage')
    return zeit.web.core.template.get_module(block)


def test_headerimage_should_have_supertitle(headerimage):
    assert headerimage.supertitle == u'Dar\xfcber spricht der Hipster'


def test_headerimage_should_have_title(headerimage):
    assert headerimage.title == u'Cinema ist das neue Panorama'


def test_headerimage_should_have_image(headerimage):
    assert zeit.content.image.interfaces.IImageGroup.providedBy(
        headerimage.image)
