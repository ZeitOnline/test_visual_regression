# -*- coding: utf-8 -*-
import datetime
import lxml.etree
import mock
import requests
import urllib
import zope.component
import pyramid.testing

import zeit.cms.interfaces

import zeit.web.core.interfaces
import zeit.web.core.template

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

def request_thread(path,
                   thread_type='full',
                   page=0,
                   page_size=4,
                   sort='asc',
                   cid=None):

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    timeout = float(conf.get('community_host_timeout_secs', 0.5))
    uri = '{}/agatho/thread{}'.format(
        conf.get('agatho_host', ''), path.encode('utf-8'))
    thread_modes = dict(
        paginated='{}_mode_top_page_{}_row_{}_sort_{}'.format(
            uri, page, page_size, sort),
        sub_thread='{}?mode=sub&cid={}'.format(uri, cid),
        deeplink='{}?mode=deeplink&cid={}&rows={}&sort={}'.format(
            uri, cid, page_size, sort),
        recommendation=('{}_mode_recommendation_'
                        'page_{}_row_{}_sort_{}').format(
                            uri, page, page_size, sort),
        promotion=('{}_mode_promotion_'
                   'page_{}_row_{}_sort_{}').format(
                        uri, page, page_size, sort))

    uri = thread_modes.get(thread_type, uri)

    try:
        with zeit.web.core.metrics.timer(
                'request_thread.community.reponse_time'):
            response = requests.get(uri, timeout=timeout)
        if response.status_code == 404:
            return
        return response.content if (200 <= response.status_code < 300) else (
            {'request_failed': datetime.datetime.utcnow()})
    except:
        return {'request_failed': datetime.datetime.utcnow()}


def test_comment_section_should_be_limited_in_top_level_comments(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    page_size = int(conf.get('comment_page_size', '10'))
    assert len(
        browser.cssselect('.comment:not(.comment--indented)')) == page_size


def test_comments_should_contain_basic_meta_data(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    comm = browser.cssselect('article.comment')[0]
    assert 'test_user' in comm.cssselect('.comment-meta__name > a')[0].text
    date = zeit.web.core.template.format_date(
        datetime.datetime(2013, 8, 17, 20, 24))
    assert date in comm.cssselect('.comment-meta__date')[0].text
    assert '#1' in comm.cssselect('.comment-meta__date')[0].text
    assert ('xyz' in (comm.cssselect('.comment__body')[0].text_content()))


def test_comments_get_thread_should_respect_top_level_sort_order(testserver):
    uid = ('http://xml.zeit.de/politik/deutschland/'
           '2013-07/wahlbeobachter-portraets/wahlbeobachter-portraets')

    comments = zeit.web.core.comments.get_thread(uid)['comments']
    assert comments[0]['created'] < comments[1]['created'], (
        'Comments are not chronological.')

    comments = zeit.web.core.comments.get_thread(uid, sort='desc')['comments']

    assert comments[0]['created'] > comments[1]['created'], (
        'Comments are not sorted most recent first.')


def test_comment_form_should_be_rendered(testbrowser, monkeypatch):
    comment = {
        'show': True,
        'show_comment_form': True,
        'show_comments': True,
        'no_comments': False,
        'note': None,
        'message': None,
        'user_blocked': False,
        'show_premoderation_warning': False
    }
    monkeypatch.setattr(
        zeit.web.site.view.CommentForm, 'comment_area', comment)
    browser = testbrowser('/zeit-online/article/01/comment-form')
    assert len(browser.cssselect('#comment-form')) == 1


def test_comment_form_should_not_be_cached(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-form')
    assert 'no-cache' in browser.headers['Cache-Control']


def test_report_form_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/article/01/report-form')
    assert len(browser.cssselect('#comment-form')) == 1


def test_comment_form_should_be_rendered_through_esi(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('include')) == 2


def test_comment_pagination_should_work(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01?page=2')
    section = browser.document.get_element_by_id('comments')
    pages = section.find_class('pager__page')
    assert len(pages) == 7
    assert '--current' in (pages[1].get('class'))


def test_comment_pagination_button_should_have_a_certain_label(testbrowser,
                                                               monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    button = browser.cssselect('.pager__button--next')
    assert button[0].text == u'Weitere Kommentare'


def test_comment_sorting_should_work(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01?sort=desc')
    comments_body = browser.document.get_element_by_id('js-comments-body')
    comments = comments_body.cssselect('.comment')
    link = browser.cssselect('.comment-preferences__item')
    assert comments[0].get('id') == 'cid-3'
    assert link[0].text_content().strip() == u'Älteste zuerst'
    assert '/zeit-online/article/01#comments' in link[0].get('href')


def test_comment_filter_links_are_present(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    assert browser.cssselect('a[href*="sort=promoted"]')
    assert browser.cssselect('a[href*="sort=recommended"]')


def test_comment_filter_links_are_activated(testbrowser, monkeypatch, testserver):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01?sort=promoted')
    assert browser.cssselect(
        'a[href*="sort=promoted"].comment-preferences__item--active')
    browser = testbrowser('/zeit-online/article/01?sort=recommended')
    assert browser.cssselect(
        'a[href*="sort=recommended"].comment-preferences__item--active')


def test_comment_filter_works_as_expected(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01?sort=promoted')
    comments = browser.cssselect('.comment')
    assert len(comments) == 1
    browser = testbrowser('/zeit-online/article/01?sort=recommended')
    comments = browser.cssselect('.comment')
    assert len(comments) == 4


def test_comment_in_reply_to_shows_origin(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    answers = browser.cssselect('.comment--indented')
    origins = browser.cssselect('.comment__origin')
    link = browser.cssselect('#cid-90 .comment__origin')[0]
    assert len(answers) == len(origins)
    assert link.text_content().strip() == 'Antwort auf #1 von test_user'


def test_comment_author_roles_should_be_displayed(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    comment_author = browser.document.get_element_by_id('cid-3')
    comment_freelancer = browser.document.get_element_by_id('cid-7')
    selector = '.comment-meta__badge--author'
    icon_author = comment_author.cssselect(selector)
    icon_freelancer = comment_freelancer.cssselect(selector)

    assert 'comment--author' in comment_author.get('class')
    assert len(icon_author) == 1
    assert len(icon_freelancer) == 1
    assert icon_author[0].attrib['title'] == 'Redaktion'
    assert icon_freelancer[0].attrib['title'] == 'Freie Autorin'


def test_comments_zon_template_respects_metadata(tplbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)

    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')

    request = mock.MagicMock()
    request.user = {'ssoid': 123, 'uid': '123', 'name': 'Max'}
    request.path_url = 'http://xml.zeit.de/zeit-online/article/01'
    request.params = {'cid': None}
    request.route_url = lambda x: "http://foo/"

    view = zeit.web.site.view_article.Article(content, request)
    view.comments_allowed = False
    comments = tplbrowser('zeit.web.site:templates/inc/article/comments.tpl',
                          view=view, request=request)
    assert len(comments.cssselect('#comments')) == 1, (
        'comment section must be present')
    assert len(comments.cssselect('article.comment')) > 0, (
        'comments must be displayed')

    form = tplbrowser('zeit.web.site:templates/inc/comments/comment-form.html',
                      view=view, request=request)
    assert len(form.cssselect('#comment-form[data-uid="123"]')) == 1, (
        'comment form tag with data-uid attribute must be present')
    assert len(form.cssselect('#comment-form textarea')) == 0, (
        'comment form must be empty')

    # reset view (kind of)
    view = zeit.web.site.view_article.Article(content, request)
    view.show_commentthread = False
    comments = tplbrowser('zeit.web.site:templates/inc/article/comments.tpl',
                          view=view, request=request)
    assert comments.contents.strip() == '', (
        'comment section template must return an empty document')


def test_comment_reply_threads_wraps_on_load_and_toggles_on_click(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/article/02' % testserver.url)

    wrapped_threads = driver.find_elements_by_css_selector('.comment--wrapped')
    assert len(wrapped_threads) == 3

    hidden_reply = driver.find_element_by_id('cid-5122767')

    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, 'cid-5122767')))
    except TimeoutException:
        assert False, 'Comment must be hidden initially'

    comment_count_overlay = driver.find_element_by_class_name(
        'comment-overlay__count')
    assert comment_count_overlay.text == '+ 2'

    wrapped_threads[0].click()
    assert len(driver.find_elements_by_css_selector('.comment--wrapped')) == 2
    assert hidden_reply.is_displayed()

    toggle = driver.find_element_by_id('hide-replies-cid-5122059')
    toggle.click()

    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, 'cid-5122767')))
    except TimeoutException:
        assert False, 'Click must hide comment reply'


def test_comment_reply_thread_must_not_wrap_if_deeplinked(
        selenium_driver, testserver, mockserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/article/02#cid-5122767' % testserver.url)
    # Force page load even if another test has left the browser on _this_ page.
    driver.refresh()
    assert driver.find_element_by_id('cid-5122767').is_displayed()


def test_comment_action_recommend_should_redirect_to_login(testserver):
    path = '/zeit-online/article/01?action=recommend&pid=2968470'
    url = testserver.url + path
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if conf.get('sso_activate'):
        pattern = '{}/anmelden?url={}'
        host = conf.get('sso_url')
    else:
        pattern = '{}/user/login?destination={}'
        host = conf.get('community_host')
    location = pattern.format(host, urllib.quote_plus(url))

    response = requests.get(url, allow_redirects=False)
    assert response.headers.get('Location', '') == location
    assert response.status_code == 303


def test_comment_area_note_should_be_displayed_if_set(
        testbrowser, monkeypatch):
    form = {
        'show_comment_form': False,
        'note': 'No community login',
        'message': None,
        'user_blocked': False,
        'show_premoderation_warning': False
    }
    monkeypatch.setattr(
        zeit.web.site.view.CommentForm, 'comment_form', form)
    browser = testbrowser('/zeit-online/article/01/comment-form')
    assert browser.cssselect('.comment-section__note div')[0].text == (
        'No community login')
    assert len(browser.cssselect('.comment-form')) == 0


def test_comment_area_should_hide_comment_form_for_invalid_logins(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.user = {
        'blocked': False,
        'premoderation': False,
        'uid': '0',
        'ssoid': '123',
        'has_community_data': True,
    }

    view = zeit.web.core.view.Content(article, request)
    assert not view.comment_area['show_comment_form']


def test_comment_area_should_hide_comment_form_no_community_response(
        application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.user = {
        'ssoid': '123',
        'has_community_data': False,
    }
    view = zeit.web.core.view.Content(article, request)
    assert not view.comment_area['show_comment_form']


def test_comment_area_should_have_comment_form(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.user = {
        'blocked': False,
        'premoderation': False,
        'has_community_data': True,
        'uid': '1',
    }
    view = zeit.web.core.view.Content(article, request)
    assert view.comment_area['show_comment_form']


def test_comment_area_should_have_login_prompt_enabled(
        application, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.core.view.Content(article, dummy_request)
    # Login prompt is rendered by comment-form template
    assert view.comment_area['show_comment_form']
    assert not view.comment_area['note']
    assert not view.comment_area['message']


def test_comment_area_should_show_message_for_blocked_users(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.user = {
        'blocked': True,
        'has_community_data': True,
        'uid': '0',
    }
    view = zeit.web.core.view.Content(article, request)
    # This is a bit implicit; the actual message is rendered by the template.
    assert not view.comment_area['note']
    assert not view.comment_area['message']


def test_article_meta_should_show_comment_count(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.comments, 'request_thread', request_thread)
    browser = testbrowser('/zeit-online/article/01')
    count = browser.cssselect('.metadata__commentcount')[0].text
    assert count == '35 Kommentare'


def test_article_meta_should_omit_comment_count_if_no_comments_present(
        testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    assert len(browser.cssselect('.metadata__commentcount')) == 0


