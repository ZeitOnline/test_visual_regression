import pytest

import gocept.lxml.objectify

import zeit.web.core.application
import zeit.web.core.source


def test_ligatus_zar_article_has_access_value(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')

    browser = testbrowser('/arbeit/article/simple-nextread')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'free'

    browser = testbrowser('/arbeit/teaser/zplus-abo')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'abo'

    browser = testbrowser('/arbeit/teaser/zplus-registration')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'registration'


def test_ligatus_zon_article_has_access_value(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')

    browser = testbrowser('/zeit-online/article/simple')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'free'

    browser = testbrowser('/zeit-online/article/zplus-zon')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'abo'

    browser = testbrowser('/zeit-online/article/zplus-zeit-register')
    meta = browser.cssselect('meta[property="ligatus:article_access_status"]')
    assert meta[0].get('content') == 'registration'


def test_ligatus_is_available_in_all_verticals(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'ligatus'
    )

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


def test_ligatus_can_be_toggled_off(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('ligatus')

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


def test_ligatus_can_be_disabled_on_article(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')

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
    ('/arbeit/article/comments?page=2', 'True'),
    ('/campus/article/02-beziehung-schluss-machen', 'False'),
    ('/campus/article/02-beziehung-schluss-machen/seite-2', 'True'),
    ('/campus/article/02-beziehung-schluss-machen/komplettansicht', 'True'),
    ('/campus/article/paginated?page=2', 'True'),
    ('/zeit-magazin/article/03', 'False'),
    ('/zeit-magazin/article/03/seite-4', 'True'),
    ('/zeit-magazin/article/03/komplettansicht', 'True'),
    ('/zeit-magazin/article/01?page=2', 'True'),
    ('/zeit-online/article/zeit', 'False'),
    ('/zeit-online/article/zeit/seite-2', 'True'),
    ('/zeit-online/article/zeit/komplettansicht', 'True'),
    ('/zeit-online/article/01?page=2', 'True')
])
def test_ligatus_indexing_only_on_first_page(testbrowser, param):
    browser = testbrowser(param[0])
    meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    assert meta[0].get('content') == param[1]


@pytest.mark.parametrize('param', [
    ('/arbeit/article/advertorial', 'True'),
    ('/campus/article/advertorial', 'True'),
    ('/zeit-magazin/article/advertorial', 'True'),
    ('/zeit-online/article/advertorial', 'True')
])
def test_ligatus_do_not_index_advertorials(testbrowser, param):
    browser = testbrowser(param[0])
    meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    assert meta[0].get('content') == param[1]


@pytest.mark.parametrize('param', [
    ('zeit-online/article/simple', 'False'),
    ('zeit-online/article/dpa', 'True')
])
def test_ligatus_do_not_index_news(testbrowser, param):
    browser = testbrowser(param[0])
    meta = browser.cssselect('meta[property="ligatus:do_not_index"]')
    assert meta[0].get('content') == param[1]


def test_ligatus_can_be_toggled_by_ressorts(monkeypatch, testbrowser):

    def mock_tree():
        return gocept.lxml.objectify.fromstring("""\
<ressorts>
  <ressort name="Arbeit" uniqueId="http://xml.zeit.de/arbeit" ligatus="no">
    <title>Arbeit</title>
  </ressort>
  <ressort name="Campus" uniqueId="http://xml.zeit.de/campus" ligatus="no">
    <title>Campus</title>
  </ressort>
  <ressort name="zeit-magazin">
    <title>Zeit Magazin</title>
  </ressort>
  <ressort name="Studium" uniqueId="http://xml.zeit.de/studium" ligatus="no">
    <title>Studium</title>
  </ressort>
</ressorts>
""")

    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')
    monkeypatch.setattr(
        zeit.web.core.source.LIGATUS_BLACKLIST.factory, '_get_tree', mock_tree)

    # ressort Arbeit: off
    browser = testbrowser('/arbeit/article/simple-nextread')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    # ressort Campus: off
    browser = testbrowser('/campus/article/simple')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    # ressort zeit-magazin: on
    browser = testbrowser('/zeit-magazin/article/header-text-only')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')


def test_ligatus_can_be_toggled_by_sub_ressort(monkeypatch, testbrowser):

    def mock_tree():
        return gocept.lxml.objectify.fromstring("""\
<ressorts>
  <ressort name="Kultur" uniqueId="http://xml.zeit.de/kultur">
    <title>Kultur</title>
    <subnavigation name="Film" uniqueId="http://xml.zeit.de/kultur/film"\
     ligatus="no">
      <title>Film &amp; TV</title>
    </subnavigation>
  </ressort>
  <ressort name="Campus" uniqueId="http://xml.zeit.de/campus">
    <title>Campus</title>
  </ressort>
</ressorts>
""")

    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')
    monkeypatch.setattr(
        zeit.web.core.source.LIGATUS_BLACKLIST.factory, '_get_tree', mock_tree)

    # subressort Film: off
    browser = testbrowser('/arbeit/article/inline-gallery')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')

    # ressort Campus: on
    browser = testbrowser('/campus/article/simple')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')


def test_ligatus_is_shown_below_special_content(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')

    browser = testbrowser('/zeit-online/video/3537342483001')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')

    browser = testbrowser('/zeit-online/gallery/biga_1')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')


def test_ligatus_is_not_shown_if_ads_disabled(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')

    browser = testbrowser('/zeit-magazin/article/nobanner')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')


def test_nextread_is_hidden_when_ligatus_is_on(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('ligatus')
    browser = testbrowser('/zeit-online/article/simple-nextread')
    assert not browser.cssselect('#nextread')
    assert browser.cssselect('#ligatus')
    assert browser.cssselect('script[src*=".ligatus.com"]')


def test_nextread_is_visible_when_ligatus_is_off(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('ligatus')
    browser = testbrowser('/zeit-online/article/simple-nextread')
    assert browser.cssselect('#nextread')
    assert not browser.cssselect('#ligatus')
    assert not browser.cssselect('script[src*=".ligatus.com"]')
