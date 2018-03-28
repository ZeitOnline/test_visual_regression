def test_ligatus_zar_article_has_access_value(testbrowser, togglepatch):
    togglepatch({'ligatus': True})

    browser = testbrowser('/arbeit/article/simple-nextread')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'free'

    browser = testbrowser('/arbeit/teaser/zplus-abo')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'abo'

    browser = testbrowser('/arbeit/teaser/zplus-registration')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'registration'


def test_ligatus_zon_article_has_access_value(testbrowser, togglepatch):
    togglepatch({'ligatus': True})

    browser = testbrowser('/zeit-online/article/simple')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'free'

    browser = testbrowser('/zeit-online/article/zplus-zon')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'abo'

    browser = testbrowser('/zeit-online/article/zplus-zeit-register')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'registration'


def test_ligatus_is_available_in_all_verticals(testbrowser, togglepatch):
    togglepatch({'ligatus': True})

    browser = testbrowser('/arbeit/article/simple-nextread')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/campus/article/simple')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-online/article/simple')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')


def test_ligatus_can_be_toggled_off(testbrowser, togglepatch):
    togglepatch({'ligatus': False})

    browser = testbrowser('/arbeit/article/simple-nextread')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/campus/article/simple')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-online/article/simple')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')


def test_ligatus_can_be_disabled_on_article(testbrowser, togglepatch):
    togglepatch({'ligatus': True})

    browser = testbrowser('/zeit-online/article/simple-ligatus-disabled')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')
    meta = browser.cssselect('meta[property="ligatus:hide_recommendations"]')
    assert meta[0].get('content') == 'True'

    browser = testbrowser('/zeit-online/article/simple')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')
    meta = browser.cssselect('meta[property="ligatus:hide_recommendations"]')
    assert meta[0].get('content') == 'False'
