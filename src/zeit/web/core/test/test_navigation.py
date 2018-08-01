import zeit.web.core.navigation


def test_navigation_item_should_accept_parameters():
    nav_item = zeit.web.core.navigation.NavigationItem(
        'foo', 'bla', 'fasel')
    assert nav_item.item_id == 'foo'
    assert nav_item.text == 'bla'
    assert nav_item.href == 'fasel'
    assert nav_item == {}


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
    nav = zeit.web.core.navigation.NavigationItem('top', '', '')
    nav_item_inner = zeit.web.core.navigation.NavigationItem(
        'inner_foo', 'inner_bla', 'inner_fasel')
    nav['inner_foo'] = nav_item_inner
    assert nav['inner_foo'].item_id == 'inner_foo'
    assert nav['inner_foo'].text == 'inner_bla'
    assert nav['inner_foo'].href == 'inner_fasel'


# This may break on config changes, so we might add some dummy data.
def test_navigation_should_be_registered(application):
    navigation = zeit.web.core.navigation.NAVIGATION_SOURCE.navigation
    assert (navigation['topnav.mainnav.4..kultur'].href ==
            'http://xml.zeit.de/kultur/index')
    assert (navigation[
            'topnav.mainnav.4..kultur']['topnav.mainnav.4.4.kunst'].text ==
            'Kunst')


def test_navigation_source_should_be_parsed(application):
    navigation = zeit.web.core.navigation.NAVIGATION_SOURCE
    assert len(navigation.navigation) == 17
    assert len(navigation.by_name) == 17


def test_navigation_classifieds_source_should_be_parsed(application):
    navigation = zeit.web.core.navigation.NAVIGATION_CLASSIFIEDS_SOURCE
    assert len(navigation.navigation) == 5


def test_navigation_services_source_should_be_parsed(application):
    navigation = zeit.web.core.navigation.NAVIGATION_SERVICES_SOURCE
    assert len(navigation.navigation) == 4


def test_navigation_footer_publisher_source_should_be_parsed(application):
    navigation = zeit.web.core.navigation.NAVIGATION_FOOTER_PUBLISHER_SOURCE
    assert len(navigation.navigation) == 3


def test_navigation_footer_links_source_should_be_parsed(application):
    navigation = zeit.web.core.navigation.NAVIGATION_FOOTER_LINKS_SOURCE
    assert len(navigation.navigation) == 2
