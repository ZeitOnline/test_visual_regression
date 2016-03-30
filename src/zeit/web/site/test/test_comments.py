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


def test_comment_section_should_be_limited_in_top_level_comments(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    page_size = int(conf.get('comment_page_size', '10'))
    assert len(
        browser.cssselect('.comment:not(.comment--indented)')) == page_size


def test_comments_should_contain_basic_meta_data(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
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


def test_comment_form_should_display_parent_hint(tplbrowser, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view.CommentForm(article, dummy_request)
    view.comment_form = {'show_comment_form': True}
    dummy_request.user = {'ssoid': 123, 'uid': '123', 'name': 'Max'}
    dummy_request.GET['pid'] = '90'

    browser = tplbrowser(
        'zeit.web.site:templates/inc/comments/comment-form.html',
        view=view, request=dummy_request)

    input = browser.cssselect('textarea[name="comment"]')[0]
    assert '"die allere..."' in input.get('placeholder')


def test_comment_form_should_not_be_cached(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-form')
    assert 'no-cache' in browser.headers['Cache-Control']


def test_report_form_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/article/01/report-form')
    assert len(browser.cssselect('#comment-form')) == 1


def test_comment_form_should_be_rendered_through_esi(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('include')) == 3


def test_comment_pagination_should_work(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread?page=2')
    pages = browser.cssselect('.pager__page')
    assert len(pages) == 7
    assert '--current' in (pages[1].get('class'))


def test_comment_pagination_button_should_have_a_certain_label(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    button = browser.cssselect('.pager__button--next')
    assert button[0].text == u'Weitere Kommentare'


def test_comment_sorting_should_work(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread?sort=desc')
    comments_body = browser.document.get_element_by_id('js-comments-body')
    comments = comments_body.cssselect('.comment')
    link = browser.cssselect('.comment-preferences__item')
    assert comments[0].get('id') == 'cid-3'
    assert link[0].text_content().strip() == u'Älteste zuerst'
    assert '/zeit-online/article/01#comments' in link[0].get('href')


def test_comment_filter_links_are_present(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    assert browser.cssselect('a[href*="sort=promoted"]')
    assert browser.cssselect('a[href*="sort=recommended"]')


def test_comment_filter_links_are_activated(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/01/comment-thread?sort=promoted')
    assert browser.cssselect(
        'a[href*="sort=promoted"].comment-preferences__item--active')
    browser = testbrowser(
        '/zeit-online/article/01/comment-thread?sort=recommended')
    assert browser.cssselect(
        'a[href*="sort=recommended"].comment-preferences__item--active')


def test_comment_filter_works_as_expected(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/01/comment-thread?sort=promoted')
    comments = browser.cssselect('.comment')
    assert len(comments) == 1
    browser = testbrowser(
        '/zeit-online/article/01/comment-thread?sort=recommended')
    comments = browser.cssselect('.comment')
    assert len(comments) == 4


def test_comment_author_roles_should_be_displayed(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
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


def test_comments_zon_template_respects_metadata(tplbrowser):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')

    request = mock.MagicMock()
    request.user = {'ssoid': 123, 'uid': '123', 'name': 'Max'}
    request.params = {'cid': None}
    request.route_url = lambda x: "http://foo/"

    view = zeit.web.site.view_article.Article(content, request)
    view.commenting_allowed = False
    comments = tplbrowser('zeit.web.site:templates/inc/comments/thread.html',
                          view=view, request=request)
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


def test_comment_reply_thread_loads_and_toggles(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/article/01' % testserver.url)
    select = driver.find_elements_by_css_selector

    first_comment_id = 'cid-3'
    first_reply_id = 'cid-90'
    second_reply_id = 'cid-91'
    last_reply_id = 'cid-92'

    assert len(select('#{}'.format(first_comment_id))) == 1
    assert len(select('#{}'.format(first_reply_id))) == 1
    assert len(select('#{}'.format(second_reply_id))) == 0
    assert len(select('#{}'.format(last_reply_id))) == 0

    # kann schlecht per ID angesprochen werden .. oder ahref selektieren?
    toggle = select('.js-load-comment-replies')[0]
    toggle.click()
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, second_reply_id)),
            expected_conditions.visibility_of_element_located(
                (By.ID, last_reply_id)))
    except TimeoutException:
        assert False, 'Click must load comment reply'

    toggle = select('.js-hide-replies')[0]
    toggle.click()
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, second_reply_id)),
            expected_conditions.invisibility_of_element_located(
                (By.ID, last_reply_id)))
    except TimeoutException:
        assert False, 'Click must hide comment reply'

    toggle = select('.comment-overlay')[0]
    toggle.click()
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, second_reply_id)),
            expected_conditions.visibility_of_element_located(
                (By.ID, last_reply_id)))
    except TimeoutException:
        assert False, 'Click must show comment reply'


# needs selenium because of esi include
def test_comment_reply_thread_loads_with_deeplink(selenium_driver, testserver):
    last_reply_id = '92'
    driver = selenium_driver
    driver.get(
        '{}/zeit-online/article/01?cid={}'
        .format(testserver.url, last_reply_id))
    select = driver.find_elements_by_css_selector
    assert len(select('#cid-{}'.format(last_reply_id))) == 1


def test_comment_actions_should_link_to_article(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    link = browser.cssselect('a.js-report-comment')[0]
    assert link.get('href') == (
        'http://localhost/zeit-online/article/01'
        '?action=report&pid=3#report-comment-form')


def test_comment_pagination_should_link_to_article(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    link = browser.cssselect('.pager__page a')[0]
    assert link.get('href') == (
        'http://localhost/zeit-online/article/01?page=2#comments')


def test_comment_pagination_should_link_to_article(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    link = browser.cssselect('.pager__page a')[0]
    assert link.get('href') == (
        'http://localhost/zeit-online/article/01?page=2#comments')


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


def test_article_meta_should_show_comment_count(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    count = browser.cssselect('.metadata__commentcount')[0].text
    assert count == '35 Kommentare'


def test_article_meta_should_omit_comment_count_if_no_comments_present(
        testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    assert len(browser.cssselect('.metadata__commentcount')) == 0


def test_comment_replies_view_renders_html_for_replies(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/01/comment-replies?cid=3&page=1&local_offset=0')
    comments = browser.cssselect('article .comment__body')
    assert len(comments) == 2
    assert 'zweite antwort' in comments[0].xpath('p')[0].text


def test_comment_displays_total_reply_count(testbrowser):
    browser = testbrowser('/zeit-online/article/01/comment-thread')
    link = browser.cssselect('.comment-overlay__count')[0]
    assert link.text == '+ 2'


def test_comment_deeplink_should_have_page_number(application):
    thread = zeit.web.core.comments.get_paginated_thread(
        'http://xml.zeit.de/zeit-online/article/01',
        cid=91)
    assert int(thread['pages']['current']) == 2

    thread = zeit.web.core.comments.get_paginated_thread(
        'http://xml.zeit.de/zeit-online/article/01',
        cid=92)
    assert int(thread['pages']['current']) == 1
