import zeit.cms.content.sources


class ToolSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'
    config_url = 'zco-toolbox-source'

    def __iter__(self):
        tree = self._get_tree()
        for node in tree.iterchildren('link'):
            yield dict(title=unicode(node.get('title')),
                       title_flyout=unicode(node.get('title_flyout')),
                       text=unicode(node.get('text')),
                       cta=unicode(node.get('cta')),
                       cta_flyout=unicode(node.get('cta_flyout')),
                       href=unicode(node.get('href')),
                       href_footer=unicode(node.get('href_footer')),
                       href_footer_text=unicode(node.get('href_footer_text')))

    @property
    def header_text(self):
        tree = self._get_tree()
        return tree.get('header')

    @property
    def footer_text(self):
        tree = self._get_tree()
        return tree.get('footer')

    @property
    def footer_link(self):
        tree = self._get_tree()
        return tree.get('href')

TOOL_SOURCE = ToolSource()


class JobMarketSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'
    config_url = 'zco-jobmarket-source'

    def __iter__(self):
        tree = self._get_tree()
        for node in tree.iterchildren('link'):
            yield dict(title_flyout=unicode(node.get('title_flyout')),
                       cta_flyout=unicode(node.get('cta_flyout')),
                       href=unicode(node.get('href')))

    @property
    def header_text(self):
        tree = self._get_tree()
        return tree.get('header')

    @property
    def footer_text(self):
        tree = self._get_tree()
        return tree.get('footer')

    @property
    def footer_link(self):
        tree = self._get_tree()
        return tree.get('href')

JOB_MARKET_SOURCE = JobMarketSource()
