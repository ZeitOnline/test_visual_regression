# -*- coding: utf-8 -*-
import lxml.etree
import mock

import zeit.cms.interfaces


def test_comments_template_respects_metadata(jinja2_env, testserver):
    url = 'http://xml.zeit.de/artikel/01'
    comments = jinja2_env.get_template(
        'zeit.web.magazin:templates/inc/article/comments.html')
    content = zeit.cms.interfaces.ICMSContent(url)
    request = mock.MagicMock()
    request.user = {'ssoid': 123}
    request.session = {'user': {'uid': '123', 'name': 'Max'}}
    request.path_url = url
    view = zeit.web.magazin.view_article.Article(content, request)
    view.content_url = url
    view.comments_allowed = False
    string = comments.render(view=view, request=request)
    html = lxml.html.fromstring(string)

    assert len(html.cssselect('#js-comments')) == 1, (
        'comment section must be present')
    assert len(html.cssselect('article.comment')) > 0, (
        'comments must be displayed')
    assert len(html.cssselect('#js-comments-form')) == 0, (
        'comment form must not be present')

    # reset view (kind of)
    view = zeit.web.magazin.view_article.Article(content, request)
    view.content_url = url
    view.show_commentthread = False
    view.linkreach = {}
    string = comments.render(view=view, request=request)

    assert string.strip() == '', (
        'comment section template must return an empty document')


def test_comments_and_replies_do_appear(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/artikel/01' % testserver.url)
    button = driver.find_element_by_class_name('js-comments-trigger')
    button.click()
    comments = driver.find_elements_by_class_name('comment')
    assert 'Ich bin ja schon etwas angejahrt' in comments[7].text
    assert 'is-indented' in comments[8].get_attribute('class')
    assert 'Man muss nicht Sozialist sein' in comments[8].text
