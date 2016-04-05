import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.article
import mock
import lxml
import pytest

def test_banner_place_should_be_serialized(application):
    place = zeit.web.core.banner.Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
                              'label': '', 'min_width': 0, 'name': 'tile_1',
                              'noscript_width_height': ['728', '90'],
                              'sizes': ['728x90'], 'tile': 1}


def test_banner_place_should_have_list_as_second_argument(application):
    with pytest.raises(IndexError):
        zeit.web.core.banner.Place(1, '123x456', True, label='')

    place = zeit.web.core.banner.Place(1, ['123x456'], True, label='')
    assert place.sizes == ['123x456']

def test_banner_list_should_be_sorted(application):
    banner_list = list(zeit.web.core.banner.BANNER_SOURCE)
    tiles = [place.tile for place in banner_list]
    assert sorted(tiles) == tiles


def test_banner_source_should_be_parsed(application):
    assert len(zeit.web.core.banner.BANNER_SOURCE) == 15
    place = list(zeit.web.core.banner.BANNER_SOURCE)[0]
    assert place.tile == 1
    assert place.sizes == ['728x90', '800x250']
    assert place.dcopt == 'ist'
    assert place.diuqilon is True

    place = list(zeit.web.core.banner.BANNER_SOURCE)[3]
    assert place.tile == 4
    assert place.sizes == ['300x250']
    assert place.dcopt is None
    assert place.diuqilon is False


def test_igd_mobile_ids_source_should_be_parsed(application):
    assert len(zeit.web.core.banner.IQD_MOBILE_IDS_SOURCE) == 4


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
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)

    # test article with xml banner is missing
    browser = testbrowser('/artikel/10')
    # desktop ads
    assert browser.cssselect('script[id^="ad-desktop-"]')


def test_inject_banner_code_should_be_inserted_on_all_pages():
    total = 10
    pages = [mock.Mock() for i in xrange(total)]

    with mock.patch.object(zeit.web.core.article,
            "_place_adtag_by_paragraph") as _place_adtag_by_paragraph:
        with mock.patch.object(zeit.web.core.article,
                "_place_content_ad_by_paragraph") as (
                    _place_content_ad_by_paragraph):
            _place_adtag_by_paragraph.return_value = True
            _place_content_ad_by_paragraph.return_value = True
            zeit.web.core.article._inject_banner_code(pages, True, False)
            assert _place_adtag_by_paragraph.call_count == total


def test_inject_banner_code_should_be_inserted_on_certain_pages():
    total = 10
    pages = [mock.Mock() for i in xrange(total)]

    with mock.patch.object(zeit.web.core.article,
                           "_place_adtag_by_paragraph") as mock_method:
        mock_method.return_value = True
        zeit.web.core.article._inject_banner_code(pages, True, True)
        assert mock_method.call_count == 1


def test_inject_banner_code_should_be_inserted_between_paragraphs(monkeypatch, application):
    tile_list = [0]
    possible_paragraphs = [1]
    monkeypatch.setattr(zeit.web.core.banner, "BANNER_SOURCE", [mock.Mock()])
    page = mock.Mock()
    setattr(page, "number", 1)
    # we need at least three paragraphs to insert AFTER 1st (before 2nd)
    page.blocks = [_create_p('This is a sample text'),
                   _create_p('This is a sample text'),
                   _create_p('This is a sample text')]
    zeit.web.core.article._place_adtag_by_paragraph(
        page, tile_list, possible_paragraphs)

    assert isinstance(page.blocks[1], zeit.web.core.block.Paragraph)
