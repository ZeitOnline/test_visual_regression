from zope.testbrowser.browser import Browser
from zeit.frontend.application import most_sufficient_teaser_tpl
from zeit.frontend.application import most_sufficient_teaser_img
import mock
import pytest
import requests
import zeit.cms.interfaces
import zeit.frontend.interfaces
import zeit.frontend.view_centerpage
import zeit.content.gallery.gallery


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

def test_centerpage_should_have_page_meta_keywords(selenium_driver, testserver):
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
              ]
    render = tpl.render(view=view, request=view.request).splitlines()
    assert render[:10] == result

def test_most_sufficient_teaser_tpl_should_produce_correct_combinations():
    should = [
        'templates/inc/teaser/teaser_lead_article_video.html',
        'templates/inc/teaser/teaser_lead_article_default.html',
        'templates/inc/teaser/teaser_lead_default_video.html',
        'templates/inc/teaser/teaser_lead_default_default.html',
        'templates/inc/teaser/teaser_default_article_video.html',
        'templates/inc/teaser/teaser_default_article_default.html',
        'templates/inc/teaser/teaser_default_default_video.html',
        'templates/inc/teaser/teaser_default_default_default.html']
    result = most_sufficient_teaser_tpl('lead', 'article', 'video')
    assert result == should

def test_autoselected_asset_from_cp_teaser_should_be_a_gallery(testserver):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset) == zeit.content.gallery.gallery.Gallery

def test_autoselected_asset_from_cp_teaser_should_be_an_image(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset) == zeit.content.image.imagegroup.ImageGroup

def test_autoselected_asset_from_cp_teaser_should_be_a_video(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset) == zeit.content.video.video.Video

def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset_2'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset[0]) == zeit.content.video.video.Video
    assert type(asset[1]) == zeit.content.video.video.Video

def test_default_teaser_should_return_default_teaser_image(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)

    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]

    teaser_img = most_sufficient_teaser_img(teaser_block, article_context)
    assert teaser_img == \
        "http://images.zeit.de/centerpage/katzencontent/katzencontent-540x304"
