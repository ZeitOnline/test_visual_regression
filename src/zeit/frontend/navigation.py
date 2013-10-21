from lxml import objectify
import pkg_resources


def get_sets():
    navigation = pkg_resources.resource_filename(__name__,
                                                 "data/navigation.xml")
    tree = objectify.parse(navigation)
    root = tree.getroot()
    top_formate = root.xpath('list[@id="top-formate"]')[0]
    sitemap = root.xpath('list[@id="sitemap"]')[0]
    sets = {'top_formate': top_formate, 'sitemap': sitemap}
    return sets
