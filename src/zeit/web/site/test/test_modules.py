import lxml.objectify
import pytest

import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zeit.content.image.interfaces

import zeit.web.core.centerpage
import zeit.web.core.utils


@pytest.fixture
def headerimage(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index-with-image')
    block = zeit.web.core.utils.find_block(
        context, module='headerimage')
    return zeit.web.core.centerpage.get_module(block)


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
    return zeit.web.core.centerpage.get_module(block)


def test_raw_xml_contains_html(rawXml):
    assert 'http://services.zeit.de/toptarif/vergleichsrechner.p' in rawXml.xml
    assert 'http://marktplatz.zeit.de/angebote/job-und-karriere' in rawXml.xml
    assert 'http://www.bellevue-ferienhaus.de/zeit/' in rawXml.xml
    assert 'http://ad-emea.doubleclick.net/clk;265976593;9126704' in rawXml.xml
    assert 'https://premium.zeit.de/?wt_mc=pm.intern.fix.zeitde.' in rawXml.xml
    assert 'https://premium.zeit.de/abo/digitalpaket' in rawXml.xml


def test_raw_xml_supports_multiple_nodes(application):
    cp = zeit.content.cp.centerpage.CenterPage()
    block = cp['lead'].create_item('xml')
    block.xml.raw.set('alldevices', 'true')
    # Setting this up is really finicky, since e.g. lxml nodes answer to list()
    # by giving out siblings with the same tag, so this is rather carefully
    # calibrated test content.
    block.xml.raw.append(lxml.objectify.XML('<p>asdf1</p>'))
    block.xml.raw.append(lxml.objectify.XML('<div>asdf2</div>'))
    module = zeit.web.core.centerpage.get_module(block)
    assert 'asdf1' in module.xml
    assert 'asdf2' in module.xml
