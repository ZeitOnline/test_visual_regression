from pytest import fixture, mark
from zeit.frontend.comments import get_thread

unique_id = u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets'


@fixture
def xml_comment(agatho):
    return agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets').xpath('//comment')[0]


@fixture
def xml_local_comment(agatho):
    return agatho.collection_get(u'http://localhost:8888/agatho/thread/artikel/03').xpath('//comment')[0]


#def test_agatho_collection_get(agatho):
#    thread = agatho.collection_get(unique_id)
#    assert thread.xpath('comment_count')[0].text == '41'
#
#
#def test_agatho_collection_get_for_nonexistent(agatho):
#    assert agatho.collection_get(u'/nosuchthread') is None
#
#
#def test_comment_as_dict(xml_comment, dummy_request):
#    from zeit.frontend.comments import comment_as_dict
#    json_comment = comment_as_dict(xml_comment, dummy_request)
#    assert json_comment['name'] == 'claudiaE'
#
#
#def test_get_entire_thread(dummy_request):
#    thread_as_json = get_thread(unique_id, dummy_request)
#    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
#    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
#    assert thread_as_json['comment_count'] == 41


def test_dict_with_article_paths_and_comment_counts_should_be_created(testserver):
    from zeit.frontend.comments import comments_per_unique_id
    # if request on node-comment-statistics fails nevertheless a dict should be return value:
    stats_path = 'data/node-comment-statistics.xmlxxx'
    comment_count_dict = comments_per_unique_id(stats_path)
    assert type(comment_count_dict) is dict
    # for test article path on existing node-comment-statistics we expect the correct commentcount:
    stats_path = 'data/node-comment-statistics.xml'
    comment_count_dict = comments_per_unique_id(stats_path)
    comments_in_article = comment_count_dict['/centerpage/article_image_asset']
    assert comments_in_article == '22'


# @mark.selenium
# def test_reply_to_comment(selenium_driver, testserver):
#     driver = selenium_driver
#     driver.get('%s/artikel/01' % testserver.url)
#     # make comments visible
#     trigger = driver.find_element_by_class_name('js-comments-trigger')
#     trigger.click()
#     # reply to comment
#     button = driver.find_element_by_class_name('js-reply-to-comment')
#     button.click()
#     driver.implicitly_wait(1)
#     cid = button.get_attribute('data-cid')
#     # pid = driver.find_element_by_css_selector("form.js-reply-form input[@name='pid']")
#     pid = driver.find_element_by_xpath("//form[@class='js-reply-form']/input[@name='pid']")
#     active = driver.switch_to_active_element()
#     textarea = driver.find_element_by_xpath("//form[@class='js-reply-form']/textarea")
#     assert pid.get_attribute('value') == cid
#     assert textarea == active
