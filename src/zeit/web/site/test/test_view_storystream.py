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

    clock.freeze(datetime.datetime(2015, 9, 27))
    browser = testbrowser('/zeit-online/storystream-teaser')

    updated = browser.cssselect('.teaser-storystream__update')
    assert len(updated) == 3

    updated_text = updated[0].text_content().strip()
    # remove multiple whitespace inside the string
    updated_text = ' '.join(updated_text.split()[1:])
    assert updated_text == 'Aktualisiert vor 1 Tag'


def test_storystream_contains_structured_data(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')

    # this "should" be done better sometimes (in the template)
    # e.g. wrap the storystream content in an article
    article = browser.cssselect('main[itemprop="mainContentOfPage"]')[0]

    assert article.cssselect('[itemprop="headline"]')
    assert article.cssselect('[itemprop="description"]')
    assert article.cssselect('[itemprop="datePublished"]')
    assert article.cssselect('[itemprop="dateModified"]')

    author = article.cssselect('[itemprop="author"]')[0]
    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == (
        'Zacharias Zacharakis')
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/Z/Zacharias_Zacharakis/index.xml')


def test_storystream_should_get_layout_from_context(testbrowser):
    # Milestone teasers are represented as <article/> instead of <div/>
    browser = testbrowser('/zeit-online/storystream/dummy')
    assert len(browser.cssselect('article.storystream-atom')) == 2
