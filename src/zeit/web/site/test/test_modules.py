import pytest

import zeit.content.cp.interfaces

import zeit.web.site.module.headerimage
import zeit.web.site.module.xml
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


def test_headerimage_should_have_complete_source(testbrowser):
    browser = testbrowser('/zeit-online/index-with-image')
    assert len(browser.cssselect('.header-image')) == 1
    assert len(browser.cssselect('.header-image__kicker')) == 1
    assert len(browser.cssselect('.header-image__title')) == 1


@pytest.fixture
def rawXml(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index-with-image')
    block = zeit.web.core.utils.find_block(
        context, module='xml')
    return zeit.web.core.template.get_module(block)


def test_raw_xml_should_have_attribute_alldevices(rawXml):
    assert rawXml.alldevices is True


def test_raw_xml_contains_html(rawXml):
    assert '<section class="servicelinks">' in rawXml.xml
    assert 'http://services.zeit.de/toptarif/vergleichsrechner.p' in rawXml.xml
    assert 'http://marktplatz.zeit.de/angebote/job-und-karriere' in rawXml.xml
    assert 'http://www.bellevue-ferienhaus.de/zeit/' in rawXml.xml
    assert 'http://ad-emea.doubleclick.net/clk;265976593;9126704' in rawXml.xml
    assert 'https://premium.zeit.de/?wt_mc=pm.intern.fix.zeitde.' in rawXml.xml
    assert 'https://premium.zeit.de/abo/digitalpaket' in rawXml.xml
