def test_zar_teaser_lead_exists(testbrowser):
    select = testbrowser('/arbeit/centerpage/teaser-lead').cssselect
    assert len(select('.teaser-lead')) == 4
