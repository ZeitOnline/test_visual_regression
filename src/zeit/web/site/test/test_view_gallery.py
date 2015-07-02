# -*- coding: utf-8 -*-

import zeit.cms.interfaces


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_zon_gallery_should_have_metadata(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.summary, .byline, .metadata')) == 3


def test_zon_gallery_should_have_no_pagination(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.pagination')) == 0


def test_zon_gallery_should_have_description(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery__description')) == 1


def test_zon_gallery_should_display_a_gallery(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery')) == 1


def test_zon_gallery_teaser_on_homepage_should_exist(
        testbrowser, testserver):
    select = testbrowser('{}/index'.format(testserver.url)).cssselect
    assert len(select('.cp-region--gallery')) == 1
    assert len(select('.cp-area--gallery')) == 1


def test_zon_gallery_teaser_on_homepage_should_have_ressort_heading(
        testbrowser, testserver):
    select = testbrowser('{}/index'.format(testserver.url)).cssselect
    title = select(
        '.cp-area--gallery > .cp-ressort-heading > \
        .cp-ressort-heading__title')
    assert len(title) == 1
    assert "Fotostrecken" in title[0].text


def test_zon_gallery_teaser_on_homepage_should_have_two_correct_teasers(
        testbrowser, testserver):

    # The structure is heavily tested because the teasers are constructed by
    # a cascade of extends and includes. We want to make sure this works.

    assumed_number_of_teasers = 2

    select = testbrowser('{}/index'.format(testserver.url)).cssselect
    teasers = select('.cp-area--gallery .zon-gallery')

    assert len(teasers) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery > .zon-gallery__figurewrapper'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery__figurewrapper > .zon-gallery__media'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery__figurewrapper > .zon-gallery__icon'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery__figurewrapper > .zon-gallery__counter'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery > .zon-gallery__container'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery__container > .zon-gallery__heading'))
    ) == assumed_number_of_teasers

    assert(len(select(
        '.zon-gallery__heading > a > .zon-gallery__kicker'))
    ) == assumed_number_of_teasers

    assert(len(select(
        '.zon-gallery__heading > a > .zon-gallery__title'))
    ) == assumed_number_of_teasers

    assert(
        len(select('.zon-gallery__container > .zon-gallery__text'))
    ) == assumed_number_of_teasers


def test_zon_gallery_teaser_on_homepage_should_hide_elements_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/index'.format(testserver.url))

    ressort_linktext = driver.find_element_by_css_selector(
        '.cp-ressort-heading__readmore-linktext')
    gallery_counter = driver.find_element_by_css_selector(
        '.zon-gallery__counter')
    gallery_text = driver.find_element_by_css_selector(
        '.zon-gallery__text')

    driver.set_window_size(480, 600)
    assert not ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext should not be displayed on mobile.')
    assert not gallery_counter.is_displayed(), (
        'Gallery image counter should not be displayed on mobile.')
    assert not gallery_text.is_displayed(), (
        'Gallery description text should not be displayed on mobile.')

    driver.set_window_size(520, 650)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on phablet.')
    assert not gallery_counter.is_displayed(), (
        'Gallery image counter should not be displayed on phablet.')
    assert not gallery_text.is_displayed(), (
        'Gallery description text should not be displayed on phablet.')

    driver.set_window_size(768, 960)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on tablet.')
    assert gallery_counter.is_displayed(), (
        'Gallery image counter must be displayed on tablet.')
    assert gallery_text.is_displayed(), (
        'Gallery description text must be displayed on tablet.')

    driver.set_window_size(980, 1024)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on desktop.')
    assert gallery_counter.is_displayed(), (
        'Gallery image counter must be displayed on desktop.')
    assert gallery_text.is_displayed(), (
        'Gallery description text must be displayed on desktop.')


def test_zon_gallery_teaser_on_homepage_should_shuffle_load_on_click(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/index'.format(testserver.url))
    teaserbutton = driver.find_element_by_css_selector(
        '.js-gallery-teaser-shuffle')
    teasertext1 = driver.find_element_by_css_selector(
        '.teaser-gallery__heading').text
    teaserbutton.click()
    driver.implicitly_wait(2)  # seconds
    teasertext2 = driver.find_element_by_css_selector(
        '.teaser-gallery__heading').text

    assert teasertext1 != teasertext2
