import datetime

import zeit.web.core.template


def test_comment_section_should_be_preliminarily_limited_to_20_entries(
        testbrowser, testserver, mockserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert len(browser.cssselect('article.comment')) == 20


def test_comments_should_contain_basic_meta_data(
        testbrowser, testserver, mockserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    comm = browser.cssselect('article.comment')[0]
    assert 'Skarsgard' in comm.cssselect('.comment__name')[0].text
    date = zeit.web.core.template.format_date_ago(
        datetime.datetime(2013, 8, 16, 20, 24))
    assert date in comm.cssselect('.comment__date-anchor')[0].text
    assert '#1' in comm.cssselect('.comment__date-anchor')[0].text
    assert ('Ein Iraner,der findet,dass die Deutschen zu wenig meckern'
            in (comm.cssselect('.comment__body')[0].text_content()))


def test_comments_get_thread_should_respect_top_level_sort_order(
        dummy_request, mockserver):
    unique_id = ('http://xml.zeit.de/politik/deutschland/'
                 '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')

    thread_chronological = zeit.web.core.comments.get_thread(
        unique_id, dummy_request)
    thread_most_recent = zeit.web.core.comments.get_thread(
        unique_id, dummy_request, reverse=True)

    assert (thread_chronological['comments'][0]['timestamp'] <
            thread_chronological['comments'][1]['timestamp'],
            'Comments are not chronological.')

    assert (thread_most_recent['comments'][0]['timestamp'] >
            thread_most_recent['comments'][1]['timestamp'],
            'Comments are not sorted most recent first.')
