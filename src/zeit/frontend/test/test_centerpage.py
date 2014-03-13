from zope.testbrowser.browser import Browser
import mock
import pytest
import zeit.cms.interfaces
import requests
import zeit.frontend.view_centerpage

def test_centerpage_should_have_correct_page_title(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    title = driver.title.strip()
    assert title == 'Lebensart - Mode, Essen und Trinken, Partnerschaft | ZEIT ONLINE'

def test_centerpage_should_have_page_meta_description(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="description"]')
    teststring = 'Die Lust am Leben: Aktuelle Berichte, Ratgeber und...'
    assert meta_description_tag.get_attribute("content").strip() == teststring

def test_centerpage_should_habe_page_meta_keywords(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath('//meta[@name="keywords"]')
    teststring = u'ZEIT ONLINE, ZEIT MAGAZIN'
    assert meta_description_tag.get_attribute("content").strip() == teststring

def test_cp_area_lead_should_have_expected_markup(jinja2_env, testserver):
    tpl = jinja2_env.get_template('templates/inc/cp_area_lead.html')
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/lebensart')

    # We need a view
    view = zeit.frontend.view_centerpage.Centerpage (cp, '')
    result = [u"<div class='area__lead'>",
              u"            <div class='teaser_block__default'>",
              u"            <div class='teaser__default'>",
              u"    <img class='teaser__default__image' src='' title='' alt='' />",
              u"    <h2 title='Gentrifizierung \u2013 Mei, is des traurig!'>",
              u"        <a href=''>",
              u"            <span class='teaser__supertitle teaser__default__supertitle'>Gentrifizierung</span>",
              u"            <span class='teaser__title teaser__default__title'>Mei, is des traurig!</span>",
              u'        </a>',
              u'    </h2>',
              u'</div>    </div>    </div>']
    assert tpl.render(view=view, request=view.request).splitlines() == result
