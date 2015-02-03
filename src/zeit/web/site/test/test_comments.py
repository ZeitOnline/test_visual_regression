def test_comment_section_should_be_preliminarily_limited_to_20_entries(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    assert len(browser.cssselect('article.comment')) <= 20


def test_comments_should_contain_basic_meta_data(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/article/01' % testserver.url)
    comm = browser.cssselect('article.comment')[0]
    assert comm.cssselect('.comment__name')[0].text == 'claudiaE'
    assert comm.cssselect('.comment__date')[0].text == 'vor 1 Jahr, 170 Tagen'
    assert comm.cssselect('.comment__anchor')[0].text == 'Kommentar #1'
    assert comm.cssselect('.comment__body')[0].text.startswith(
        'Vor allen Wahlen werden die Voraussetzungen einer Wahlbeteiligung')
