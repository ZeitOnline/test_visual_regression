from pytest import fixture
from zeit.frontend.comments import get_thread

unique_id = u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets'


@fixture
def xml_comment(agatho):
    return agatho.collection_get(u'http://xml.zeit.de/politik/deutschland/2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets').xpath('//comment')[0]


@fixture
def xml_local_comment(agatho):
    return agatho.collection_get(u'http://localhost:8888/agatho/thread/artikel/03').xpath('//comment')[0]


def test_agatho_collection_get(agatho):
    thread = agatho.collection_get(unique_id)
    assert thread.xpath('comment_count')[0].text == '41'


def test_agatho_collection_get_for_nonexistent(agatho):
    assert agatho.collection_get(u'/nosuchthread') is None


def test_comment_as_dict(xml_comment, dummy_request):
    from zeit.frontend.comments import comment_as_dict
    json_comment = comment_as_dict(xml_comment, dummy_request)
    assert json_comment['name'] == 'claudiaE'


def test_get_entire_thread(dummy_request):
    thread_as_json = get_thread(unique_id, dummy_request)
    assert thread_as_json['comments'][0]['name'] == 'claudiaE'
    assert thread_as_json['comments'][40]['name'] == 'Galgenstein'
    assert thread_as_json['comment_count'] == 41

def test_reply_to_comment(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    # make comments visible
    trigger = driver.find_element_by_id('js-comments-trigger')
    trigger.click()
    # reply to comment
    button = driver.find_element_by_class_name('js-reply-to-comment')
    cid = button.get_attribute('data-cid')
    pid = driver.find_element_by_name('pid')
    button.click()
    active = driver.switch_to_active_element()
    textarea = driver.find_element_by_name('comment')
    assert pid.get_attribute('value') == cid
    assert textarea == active
