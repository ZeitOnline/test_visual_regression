def test_check_product_id_campaign_paywall_webtrekk(testbrowser):
    browser = testbrowser('/zeit-online/article/01?C1-Meter-Status=paywall')

    wt_zmc = browser.cssselect('form input[name="wt_zmc"]')[0]
    wt_val = wt_zmc.get('value')
    wt_ck = 'fix.int.zonaudev.diezeit.wall_abo.premium.bar_metered.link.zede'
    assert wt_val == wt_ck

    utm_content = browser.cssselect('form input[name="utm_content"]')[0]
    utm_val = utm_content.get('value')
    utm_ck = 'premium_bar_metered_link_zede'
    assert utm_val == utm_ck
