def test_rss_feed_extracts_social_fields(testbrowser, testserver):
    feed_url = '%s/centerpage/index/rss-socialflow-twitter' % testserver.url
    browser = testbrowser(feed_url)
    assert browser.headers['Content-Type'].startswith('application/rss+xml')
    feed = browser.contents
    assert '<atom:link href="%s"' % feed_url in feed
    assert ('<link>http://www.zeit.de/centerpage/article_image_asset</link>'
            in feed)
    assert '<content:encoded>Twitter-Text' in feed
    assert '<content:encoded>Facebook-Text' not in feed

    feed_url = '%s/centerpage/index/rss-socialflow-facebook' % testserver.url
    browser = testbrowser(feed_url)
    feed = browser.contents
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' in feed
