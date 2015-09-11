import requests


def test_rss_feed_extracts_social_fields(testserver):
    feed_path = '/centerpage/index/rss-socialflow-twitter'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})

    assert res.status_code == 200
    assert res.headers['Content-Type'].startswith('application/rss+xml')
    feed = res.text
    assert '<atom:link href="http://newsfeed.zeit.de%s"' % feed_path in feed
    assert ('<link>http://www.zeit.de/centerpage/article_image_asset</link>'
            in feed)
    assert '<content:encoded>Twitter-Text' in feed
    assert '<content:encoded>Facebook-Text' not in feed

    feed_path = '/centerpage/index/rss-socialflow-facebook'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    feed = res.text
    assert '<content:encoded>Twitter-Text' not in feed
    assert '<content:encoded>Facebook-Text' in feed
