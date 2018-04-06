import collections

import zc.sourcefactory.source

import zeit.cms.content.sources

import zeit.web.core.cache
import zeit.web.core.utils

CONFIG_CACHE = zeit.web.core.cache.get_region('config')


class NavigationItem(collections.OrderedDict):
    """The navigation is a tree structure, i.e. items may contain other items.
    """

    def __init__(self, item_id, text, href, label=None):
        super(NavigationItem, self).__init__()
        self.item_id = item_id
        self.text = text
        self.href = href
        self.label = label


class NavigationSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-source'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        @property
        def navigation(self):
            return self.factory.compile_navigation()

        @property
        def by_name(self):
            return self.factory.compile_navigation_by_name()

    @CONFIG_CACHE.cache_on_arguments()
    def compile_navigation(self):
        navigation = NavigationItem('root', '', '')
        root = self._get_tree()
        self._register_navigation_items(navigation, root.iterfind('section'))
        return navigation

    def _register_navigation_items(self, navigation, node):
        for section in node:
            item_id = section.find('link').get('id')
            text = section.find('link').text
            href = zeit.web.core.utils.maybe_convert_http_to_https(
                section.find('link').get('href'))
            label = section.find('link').get('label') or None
            navigation[item_id] = NavigationItem(item_id, text, href, label)
            try:
                sub_sections_node = section.find(
                    'sub_sections').iterfind('sub_section')
                self._register_navigation_items(
                    navigation[item_id], sub_sections_node)
            except AttributeError:
                pass

    @CONFIG_CACHE.cache_on_arguments()
    def compile_navigation_by_name(self):
        navigation_links = NavigationItem('root', '', '')
        navigation = self.compile_navigation()
        for n in navigation:
            nav_item = navigation[n]
            navigation_links[nav_item.text.lower()] = {}
            navigation_links[nav_item.text.lower()]['link'] = nav_item.href
            navigation_links[nav_item.text.lower()]['text'] = nav_item.text

        return navigation_links

NAVIGATION_SOURCE = NavigationSource()(None)


class NavigationClassifiedsSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-classifieds-source'

NAVIGATION_CLASSIFIEDS_SOURCE = NavigationClassifiedsSource()(None)


class NavigationServicesSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-services-source'

NAVIGATION_SERVICES_SOURCE = NavigationServicesSource()(None)


class NavigationFooterPublisherSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-footer-publisher-source'

NAVIGATION_FOOTER_PUBLISHER_SOURCE = NavigationFooterPublisherSource()(None)


class NavigationFooterLinksSource(NavigationSource):

    product_configuration = 'zeit.web'
    config_url = 'navigation-footer-links-source'

NAVIGATION_FOOTER_LINKS_SOURCE = NavigationFooterLinksSource()(None)


class NavigationMoreLinksSource(NavigationSource):
    product_configuration = 'zeit.web'
    config_url = 'navigation-more-source'
NAVIGATION_MORE_SOURCE = NavigationMoreLinksSource()(None)
