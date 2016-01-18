import collections

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
