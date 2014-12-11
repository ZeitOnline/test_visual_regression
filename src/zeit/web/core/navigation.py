import collections

import lxml.objectify
import urllib2
import zope.interface

import zeit.web.core.interfaces


@zope.interface.implementer(zeit.web.core.interfaces.INavigation)
class Navigation(object):

    def __init__(self):
        self.navigation_items = collections.OrderedDict()

    def __contains__(self, item):
        return item in self.navigation_items

    def __iter__(self):
        return iter(self.navigation_items)

    def __setitem__(self, key, value):
        self.navigation_items[key] = value

    def __getitem__(self, key):
        return self.navigation_items[key]

    def __delitem__(self, key):
        del self.navigation_items[key]

    def has_children(self):
        return len(self.navigation_items) > 0


@zope.interface.implementer(zeit.web.core.interfaces.INavigationItem)
class NavigationItem(Navigation):

    def __init__(self, item_id, text, href):
        super(NavigationItem, self).__init__()
        self.item_id = item_id
        self.text = text
        self.href = href


navigation = None
navigation_services = None
navigation_classifieds = None
navigation_footer_publisher = None
navigation_footer_links = None


def make_navigation(navigation_config):
    navigation = Navigation()

    try:
        config_file = urllib2.urlopen(navigation_config)
    except (urllib2.URLError, ValueError):
        return navigation

    root = lxml.objectify.fromstring(config_file.read())
    _register_navigation_items(navigation, root.xpath('section'))

    return navigation


def _register_navigation_items(navigation, node):
    for section in node:
        item_id = section.link.attrib.get('id')
        text = section.link.text
        href = section.link.attrib.get('href')
        navigation[item_id] = NavigationItem(
            item_id, text, href)
        try:
            sub_sections_node = section.sub_sections.xpath('sub_section')
            _register_navigation_items(
                navigation[item_id], sub_sections_node)
        except AttributeError:
            pass
