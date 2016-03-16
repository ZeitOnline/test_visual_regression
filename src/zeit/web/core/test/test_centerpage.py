import mock


def test_topic_teaser_contain_expected_structure(tplbrowser):
    view = mock.Mock()
    view.package = 'zeit.web.site'
    area = mock.Mock()
    area.values.return_value = [0, 1, 2, 3]
    browser = tplbrowser(
        'zeit.web.core:templates/inc/area/topic.html', area=area, view=view)
    assert browser.cssselect('section.teaser-topic')
    assert browser.cssselect('div.teaser-topic-list')
