import datetime

import zeit.web.core.template


def test_comment_section_should_be_preliminarily_limited_to_20_entries(
        testbrowser, testserver, monkeyagatho):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert len(browser.cssselect('article.comment')) == 20


def test_comments_should_contain_basic_meta_data(
        testbrowser, testserver, monkeyagatho):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    comm = browser.cssselect('article.comment')[0]
    assert 'claudiaE' in comm.cssselect('.comment__name')[0].text
    date = zeit.web.core.template.format_date_ago(
        datetime.datetime(2013, 8, 17, 13, 18))
    assert date in comm.cssselect('.comment__date')[0].text
    assert '#1' in comm.cssselect('.comment__anchor')[0].text
    assert ('Vor allen Wahlen werden die Voraussetzungen einer Wahlbeteiligung'
            in (comm.cssselect('.comment__body')[0].text_content()))
