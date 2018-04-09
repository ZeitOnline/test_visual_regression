import zeit.content.article.interfaces
import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.article

import mock
import lxml


def test_banner_id_mappings_source_should_be_parsed(application):
    assert len(
        zeit.web.core.banner.BANNER_ID_MAPPINGS_SOURCE) == 22


def _create_p(text):
    model_block = mock.Mock()
    model_block.xml = lxml.etree.fromstring(u'<p>{}</p>'.format(text))
    return zeit.web.core.block.Paragraph(model_block)


def test_paragraphs_should_be_filtered_by_length():
    ps = [_create_p('This is a slightly longer p')]
    assert len(zeit.web.core.article._paragraphs_by_length(ps, 1)) == 1
    assert len(zeit.web.core.article._paragraphs_by_length(ps, 30)) == 0

    ps = []
    for x in range(2):
        ps.append(_create_p('{}. p'))

    assert len(zeit.web.core.article._paragraphs_by_length(ps, 1)) == 2
    assert len(zeit.web.core.article._paragraphs_by_length(ps, 5)) == 1

    ps = []
    for x in range(4):
        ps.append(_create_p('{}. p'))

    assert len(zeit.web.core.article._paragraphs_by_length(ps, 1)) == 4
    assert len(zeit.web.core.article._paragraphs_by_length(ps, 5)) == 2

    ps = []
    for x in range(5):
        ps.append(_create_p('{}. p'))

    assert len(zeit.web.core.article._paragraphs_by_length(ps, 1)) == 5
    assert len(zeit.web.core.article._paragraphs_by_length(ps, 5)) == 2


def test_banner_should_be_displayed_on_article_when_banner_xml_is_missing(
        testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')

    # test article with xml banner is missing
    browser = testbrowser('/zeit-magazin/article/10')
    # desktop ads
    assert browser.cssselect('script[id^="ad-desktop-"]')


def test_inject_banner_code_should_be_inserted_on_all_pages(
        application, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/paginated')
    with mock.patch.object(
            zeit.web.core.article,
            "_paragraphs_by_length") as _paragraphs_by_length:
        _paragraphs_by_length.return_value = []
        pages = zeit.web.core.article.pages_of_article(
            article, advertising_enabled=True)
        count = _paragraphs_by_length.call_count
    assert count == len(pages)
