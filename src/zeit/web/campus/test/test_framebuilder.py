# -*- coding: utf-8 -*-


def test_framebuilder_should_inline_svgs(testbrowser):
    browser = testbrowser('/campus/framebuilder')
    assert len(browser.xpath(
        '/html/body/div[@class="invisible"]/svg/symbol')) == 5
    for item in browser.cssselect('header.header svg > use'):
        assert item.attrib['xlink:href'].startswith('#')
