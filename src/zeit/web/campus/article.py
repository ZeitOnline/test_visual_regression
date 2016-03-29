import zeit.content.article
import zope.interface


@zope.interface.implementer(zeit.web.core.interfaces.IPage)
class Page(zeit.web.core.article.Page):

    def get_content_ad(self):
        return 'stoas-artikelanker'
