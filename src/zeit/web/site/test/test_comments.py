# -*- coding: utf-8 -*-
import datetime
import zope.component

import zeit.web.core.interfaces
import zeit.web.core.template


def test_comment_section_should_be_limited(testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    page_size = int(conf.get('comment_page_size', '10'))
    assert len(browser.cssselect('article.comment')) == page_size


def test_comments_should_contain_basic_meta_data(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    comm = browser.cssselect('article.comment')[0]
    assert 'Skarsgard' in comm.cssselect('.comment__name')[0].text
    date = zeit.web.core.template.format_date(
        datetime.datetime(2013, 8, 16, 20, 24))
    assert date in comm.cssselect('.comment__date')[0].text
    assert '#1' in comm.cssselect('.comment__date')[0].text
    assert ('Ein Iraner,der findet,dass die Deutschen zu wenig meckern'
            in (comm.cssselect('.comment__body')[0].text_content()))


def test_comments_get_thread_should_respect_top_level_sort_order(
        dummy_request, testserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')

    thread_chronological = zeit.web.core.comments.get_thread(
        unique_id, dummy_request)
    thread_most_recent = zeit.web.core.comments.get_thread(
        unique_id, dummy_request, sort='desc')

    assert (thread_chronological['comments'][0]['timestamp'] <
            thread_chronological['comments'][1]['timestamp'],
            'Comments are not chronological.')

    assert (thread_most_recent['comments'][0]['timestamp'] >
            thread_most_recent['comments'][1]['timestamp'],
            'Comments are not sorted most recent first.')


def test_comment_form_should_be_rendered(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01?form=comment' %
                          testserver.url)
    assert len(browser.cssselect('#comment-form')) == 1


def test_comment_form_should_be_rendered_through_esi(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert len(browser.cssselect('include')) == 1
