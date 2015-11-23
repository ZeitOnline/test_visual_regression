import collections

import lxml.objectify
import requests
import requests.exceptions
import requests_file
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

    def __init__(self, item_id, text, href, label=None):
        super(NavigationItem, self).__init__()
        self.item_id = item_id
        self.text = text
        self.href = href
        self.label = label


navigation = None
navigation_by_name = None
navigation_services = None
navigation_classifieds = None
navigation_footer_publisher = None
navigation_footer_links = None


def make_navigation(navigation_config):
    navigation = Navigation()
    # XXX requests does not seem to allow to mount stuff as a default, sigh.
    session = requests.Session()
    session.mount('file://', requests_file.FileAdapter())
    try:
        config_file = session.get(navigation_config, stream=True, timeout=2)
        # Analoguous to requests.api.request().
        session.close()
    except requests.exceptions.RequestException:
        return navigation

    root = lxml.objectify.parse(config_file.raw).getroot()
    _register_navigation_items(navigation, root.xpath('section'))

    return navigation


def make_navigation_by_name(navigation_config):
    navigation_links = Navigation()
    for n in navigation:
        nav_item = navigation[n]
        navigation_links[nav_item.text.lower()] = {}
        navigation_links[nav_item.text.lower()]['link'] = nav_item.href
        navigation_links[nav_item.text.lower()]['text'] = nav_item.text
    return navigation_links


def _register_navigation_items(navigation, node):
    for section in node:
        item_id = section.link.attrib.get('id')
        text = section.link.text
        href = section.link.attrib.get('href')
        label = section.link.attrib.get('label') or None
        navigation[item_id] = NavigationItem(
            item_id, text, href, label)
        try:
            sub_sections_node = section.sub_sections.xpath('sub_section')
            _register_navigation_items(
                navigation[item_id], sub_sections_node)
        except AttributeError:
            pass
