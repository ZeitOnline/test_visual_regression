import zeit.web.core.banner
import zeit.web.core.article
import mock
import lxml


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
