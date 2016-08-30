import zeit.content.cp.centerpage

import zeit.web.core.centerpage


def test_ranking_area_with_automatic_false_has_zero_hits(application):
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = 'http://xml.zeit.de/testcp'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'ranking'
    area.count = 1
    area.automatic_type = 'query'
    area.raw_query = 'any'
    area.automatic = False
    area = zeit.web.core.centerpage.get_area(area)
    assert area.hits == 0
