# -*- coding: utf-8 -*-
import datetime


def test_storystream_page_should_render_headerimage(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    assert len(browser.cssselect('.storystream-headerimage')) == 1


def test_storystream_page_should_render_scope(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    scope = browser.cssselect('.storystream-scope__dates')
    scope_text = scope[0].text_content().strip()
    assert scope_text == '25. Januar 2015 bis 5. Juli 2015'


def test_storystream_page_should_render_label(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    assert len(browser.cssselect(
               '.storystream-headerimage__kicker-label')) == 1


def test_storystream_teaser_should_render_teaser_types(testbrowser):
    browser = testbrowser('/zeit-online/storystream-teaser')
    assert len(browser.cssselect('.cp-region--solo .teaser-storystream')) == 1
    assert len(browser.cssselect('.cp-region--duo .teaser-storystream')) == 2
    assert len(browser.cssselect('.teaser-storystream--in-area-minor')) == 1


def test_storystream_teaser_should_hide_age_for_old_storystreams(testbrowser):
    browser = testbrowser('/zeit-online/storystream-teaser')
    updated = browser.cssselect('.teaser-storystream__update')
    assert len(updated) == 0


def test_storystream_teaser_should_show_age_for_new_storystreams(
        testbrowser, clock):

    clock.freeze(datetime.datetime(2015, 6, 27))
    browser = testbrowser('/zeit-online/storystream-teaser')

    updated = browser.cssselect('.teaser-storystream__update')
    assert len(updated) == 3

    updated_text = updated[0].text_content().strip()
    # remove multiple whitespace inside the string
    updated_text = ' '.join(updated_text.split()[1:])
    assert updated_text == 'Aktualisiert vor 1 Tag'


def test_storystream_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-online/storystream/dummy').structured_data()

    page = data['WebPage']
    article = data['Article']
    itemlist = data['ItemList']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEIT ONLINE'
    assert publisher['url'] == 'http://localhost/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zon.png')
    assert publisher['logo']['width'] == 565
    assert publisher['logo']['height'] == 60

    # check BreadcrumbList
    assert len(breadcrumb['itemListElement']) == 2

    for index, item in enumerate(breadcrumb['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        if index == 1:
            assert item['item']['@id'] == 'http://localhost/'
            assert item['item']['name'] == 'ZEIT ONLINE'
        elif index == 2:
            assert item['item']['@id'] == 'http://localhost/politik/index'
            assert item['item']['name'] == 'Politik'

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-online/storystream/dummy')
    assert article['headline'] == u'Griechenland: Das linke Experiment'
    assert len(article['description'])
    assert article['datePublished'] == '2015-06-11T12:09:57+02:00'
    assert article['dateModified'] == '2015-07-05T07:40:50+00:00'
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/zeit-online/image/stress-frau-springen/'
        'wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Zacharias Zacharakis'
    assert article['author']['url'] == (
        'http://localhost/autoren/Z/Zacharias_Zacharakis/index.xml')

    # check ItemList
    assert len(itemlist['itemListElement']) == 5

    for index, item in enumerate(itemlist['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        assert item['url'].startswith('http://localhost/zeit-online/')


def test_storystream_should_get_layout_from_context(testbrowser):
    # Milestone teasers are represented as <article/> instead of <div/>
    browser = testbrowser('/zeit-online/storystream/dummy')
    assert len(browser.cssselect('article.storystream-atom')) == 4


def test_storystream_in_article_should_have_correct_order(testbrowser):
    url1 = '/zeit-online/storystream/articles/griechenland-referendum-oxi'
    browser = testbrowser(url1)
    assert len(browser.cssselect('.storystream-in-article a')) == 3
    itemlist = browser.cssselect('.storystream-in-article__list')
    items = itemlist[0].getchildren()
    assert len(items) == 5
    assert items[0].text == 'Dieser Artikel'
    assert items[2].text == 'zuvor'

    url2 = '/zeit-online/storystream/articles/grexit-griechenland-euro-zone'
    browser = testbrowser(url2)
    assert len(browser.cssselect('.storystream-in-article a')) == 3
    itemlist = browser.cssselect('.storystream-in-article__list')
    items = itemlist[0].getchildren()
    assert len(items) == 6
    assert items[0].text == 'danach'
    assert items[2].text == 'Dieser Artikel'
    assert items[4].text == 'zuvor'

    url3 = '/zeit-online/storystream/articles/syriza-tsipras-parlamentswahl'
    browser = testbrowser(url3)
    assert len(browser.cssselect('.storystream-in-article a')) == 3
    itemlist = browser.cssselect('.storystream-in-article__list')
    items = itemlist[0].getchildren()
    assert len(items) == 5
    assert items[0].text == 'danach'
    assert items[3].text == 'Dieser Artikel'


def test_storystream_in_article_should_show_no_teaser_on_mobile(
        selenium_driver, testserver):
    url = '/zeit-online/storystream/articles/griechenland-referendum-oxi'
    driver = selenium_driver
    driver.get('{}{}'.format(testserver.url, url))

    small_teaser = driver.find_element_by_css_selector(
        '.storystream-in-article-teaser')

    driver.set_window_size(320, 480)
    assert not small_teaser.is_displayed(), (
        'Small teaser for storystream teaser should be hidden on mobile.')

    driver.set_window_size(1000, 1024)
    assert small_teaser.is_displayed(), (
        'Small teaser for storystream teaser should be visible on desktop.')


def test_storystream_atom_should_show_no_fallback_image(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    teaser = browser.cssselect('article.storystream-atom')
    images = browser.cssselect('article.storystream-atom img')

    assert len(teaser) == 4
    assert not [x for x in images if '/default/teaser_image/' in x.get('src')]


def test_storystream_update_date_in_header(testbrowser):
    browser = testbrowser('zeit-online/storystream/dummy')
    updateddate = browser.cssselect(
        '.storystream-headerimage__date')[0].text.strip()
    modifieddate = browser.cssselect(
        '.storystream-scope__link')[1].text.strip()
    assert updateddate == modifieddate
