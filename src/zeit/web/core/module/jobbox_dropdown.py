import zope.security.proxy

import zeit.cms.content.sources


class Job(object):

    def __init__(self, id=None, title=None, href=None):
        self.id = id
        self.title = title
        self.href = href

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.id == other.id


class JobboxDropdownSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'

    def __init__(self, config_url):
        self.config_url = config_url

    def __iter__(self):
        tree = self._get_tree()
        yield [Job(
            unicode(job.get('id')),
            unicode(job.get('title')),
            unicode(job.text.strip()))
            for job in tree.xpath('//job')]

    def get_info(self, type):
        tree = self._get_tree()
        element = tree.xpath('//{}'.format(type))[0]
        return {
            'id': unicode(element.get('id')),
            'title': unicode(element.get('title')),
            'link': unicode(element.text.strip())
        }


class JobboxDropdown(zeit.web.core.centerpage.Module):

    source = NotImplemented
    title = NotImplemented

    @zeit.web.reify
    def jobs(self):
        return iter(self.source)

    @zeit.web.reify
    def button(self):
        return JobboxDropdownSource.get_info(self.source, 'defaultLink')

    @zeit.web.reify
    def link(self):
        return JobboxDropdownSource.get_info(self.source, 'mailLink')