import zeit.web.core.application
import zeit.web.core.navigation


def test_navigation_item_should_accept_parameters():
    nav_item = zeit.web.core.navigation.NavigationItem(
        'foo', 'bla', 'fasel')
    assert nav_item.item_id == 'foo'
    assert nav_item.text == 'bla'
    assert nav_item.href == 'fasel'
    assert nav_item.navigation_items == {}


def test_navigation_items_should_be_extensible():
    nav_item = zeit.web.core.navigation.NavigationItem(
        'foo', 'bla', 'fasel')
    nav_item_inner = zeit.web.core.navigation.NavigationItem(
        'inner_foo', 'inner_bla', 'inner_fasel')
    nav_item['inner_foo'] = nav_item_inner
    assert nav_item['inner_foo'].item_id == 'inner_foo'
    assert nav_item['inner_foo'].text == 'inner_bla'
    assert nav_item['inner_foo'].href == 'inner_fasel'


def test_navigation_items_should_be_addable_to_navigation():
    nav = zeit.web.core.navigation.Navigation()
    nav_item_inner = zeit.web.core.navigation.NavigationItem(
        'inner_foo', 'inner_bla', 'inner_fasel')
    nav['inner_foo'] = nav_item_inner
    assert nav['inner_foo'].item_id == 'inner_foo'
    assert nav['inner_foo'].text == 'inner_bla'
    assert nav['inner_foo'].href == 'inner_fasel'


# This may break on config changes, so we might add some dummy data.
def test_navigation_should_be_registered(application):
    navigation = zeit.web.core.sources.NAVIGATION_SOURCE.navigation
    assert (navigation['topnav.mainnav.4..kultur'].href ==
            'http://xml.zeit.de/kultur/index')
    assert (navigation[
            'topnav.mainnav.4..kultur']['topnav.mainnav.4.4.kunst'].text ==
            'Kunst')
