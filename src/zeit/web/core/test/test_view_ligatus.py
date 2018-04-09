import pytest


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
    togglepatch({
        'ligatus': True,
        'ligatus_on_arbeit': True,
        'ligatus_on_campus': True,
        'ligatus_on_magazin': True,
        'ligatus_on_site': True
    })

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
    togglepatch({'ligatus': True, 'ligatus_on_site': True})

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


def test_ligatus_indexing_can_be_disabled_on_article(testbrowser):
    # not yet implemented
    # browser = testbrowser('/zeit-online/article/simple-ligatus-donotindex')
    # meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    # assert meta[0].get('content') == 'True'

    browser = testbrowser('/zeit-online/article/simple')
    meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    assert meta[0].get('content') == 'False'


@pytest.mark.parametrize(
    'parameter', [
        ('/arbeit/article/simple', 'arbeit'),
        ('/arbeit/article/column', 'arbeit'),
        ('/campus/article/simple', 'studium'),
        ('/campus/article/citation', 'studium'),
        ('/zeit-magazin/article/01', 'zeit-magazin'),
        ('/zeit-magazin/article/authorbox', 'zeit-magazin'),
        ('/zeit-online/article/simple', 'sport'),
        ('/zeit-online/article/zeit', 'gesellschaft')
    ])
def test_ligatus_has_ressort(testbrowser, parameter):
    browser = testbrowser(parameter[0])
    metatag = browser.cssselect('meta[property="ligatus:section"]')
    assert metatag[0].get('content') == parameter[1]


@pytest.mark.parametrize(
    'parameter', [
        ('/zeit-online/cp-content/taglogo/article-d18-tag',
            'D18, 70 Jahre DIE ZEIT'),
        ('/zeit-online/cp-content/taglogo/article-campus-d17-tag',
            'D17, In der Mensa mit'),
        ('/arbeit/article/series', '70 Jahre DIE ZEIT'),
        ('/zeit-magazin/article/liebeskolumne-rationalitaet-emotionen',
            'Liebeskolumne'),
        ('/zeit-online/article/serie-eilmeldung', '70 Jahre DIE ZEIT'),
        ('/zeit-online/cp-content/taglogo/article-zplus-d17-tag', 'D17')
    ])
def test_ligatus_has_special(testbrowser, parameter):
    browser = testbrowser(parameter[0])
    metatag = browser.cssselect('meta[property="ligatus:special"]')
    assert metatag[0].get('content') == parameter[1]


def test_ligatus_has_no_tag_when_special_is_missing(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    assert not browser.cssselect('meta[property="ligatus:special"]')

    browser = testbrowser('/arbeit/article/simple')
    assert not browser.cssselect('meta[property="ligatus:special"]')

    browser = testbrowser('/campus/article/simple')
    assert not browser.cssselect('meta[property="ligatus:special"]')

    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert not browser.cssselect('meta[property="ligatus:special"]')


@pytest.mark.parametrize('param', [
    ('/arbeit/article/paginated', 'False'),
    ('/arbeit/article/paginated/seite-3', 'True'),
    ('/arbeit/article/paginated/komplettansicht', 'True'),
    ('/campus/article/02-beziehung-schluss-machen', 'False'),
    ('/campus/article/02-beziehung-schluss-machen/seite-2', 'True'),
    ('/campus/article/02-beziehung-schluss-machen/komplettansicht', 'True'),
    ('/zeit-magazin/article/03', 'False'),
    ('/zeit-magazin/article/03/seite-4', 'True'),
    ('/zeit-magazin/article/03/komplettansicht', 'True'),
    ('/zeit-online/article/zeit', 'False'),
    ('/zeit-online/article/zeit/seite-2', 'True'),
    ('/zeit-online/article/zeit/komplettansicht', 'True')
])
def test_ligatus_indexing_only_on_first_page(testbrowser, param):
    browser = testbrowser(param[0])
    meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    assert meta[0].get('content') == param[1]


def test_ligatus_can_be_toggled_globally(testbrowser, togglepatch):
    togglepatch({
        'ligatus': False,
        'ligatus_on_arbeit': True,
        'ligatus_on_campus': True,
        'ligatus_on_magazin': True,
        'ligatus_on_site': True
    })

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


def test_ligatus_can_be_toggled_for_verticals(testbrowser, togglepatch):
    togglepatch({
        'ligatus': True,
        'ligatus_on_arbeit': True,
        'ligatus_on_campus': False,
        'ligatus_on_magazin': False,
        'ligatus_on_site': True
    })

    browser = testbrowser('/arbeit/article/simple-nextread')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/campus/article/simple')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-online/article/simple')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')
