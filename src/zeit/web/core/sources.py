import logging
import xml.sax.saxutils

import zeit.cms.content.sources
import zeit.cms.interfaces


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


class VideoSeriesSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.web'
    config_url = 'series-source'

    def getValues(self):
        try:
            tree = self._get_tree()
        except (TypeError, IOError):
            return []
        videoseries = tree.xpath('/allseries/videoseries/series')
        result = []
        for node in videoseries:
            result.append(dict(url=node.get('url'), title=node.get('title')))
        return result

VIDEO_SERIES = VideoSeriesSource()


class RessortFolderSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = (
        zeit.cms.content.sources.SubNavigationSource.product_configuration)
    config_url = zeit.cms.content.sources.SubNavigationSource.config_url

    master_node_xpath = (
        zeit.cms.content.sources.SubNavigationSource.master_node_xpath)
    slave_tag = zeit.cms.content.sources.SubNavigationSource.slave_tag
    attribute = zeit.cms.content.sources.SubNavigationSource.attribute

    # Same idea as zeit.cms.content.sources.MasterSlavesource.getTitle()
    def find(self, ressort, subressort):
        tree = self._get_tree()
        if not subressort:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    master=xml.sax.saxutils.quoteattr(ressort)))
        else:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'
                u'/{slave_tag}[@{attribute} = {slave}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    slave_tag=self.slave_tag,
                    master=xml.sax.saxutils.quoteattr(ressort),
                    slave=xml.sax.saxutils.quoteattr(subressort)))
        if not nodes:
            return {}
        return zeit.cms.interfaces.ICMSContent(
            nodes[0].get('uniqueId'), {})

RESSORTFOLDER_SOURCE = RessortFolderSource()
