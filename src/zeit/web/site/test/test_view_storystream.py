# -*- coding: utf-8 -*-
import datetime


def test_storystream_page_should_render_headerimage(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    assert len(browser.cssselect('.storystream-headerimage')) == 1


def test_storystream_page_should_render_scope(testbrowser):
    browser = testbrowser('/zeit-online/storystream/dummy')
    scope = browser.cssselect('.storystream-scope__dates')
    scope_text = scope[0].text_content().strip()
    assert scope_text == '25. Januar 2015 bis 19. September 2015'


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
    updated_text = ' '.join(updated_text.split())
    assert updated_text == 'Aktualisiert vor 1 Tag'
