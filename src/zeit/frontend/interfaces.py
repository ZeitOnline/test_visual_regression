import zope.interface
import zope.interface.common.sequence


class IPages(zope.interface.common.sequence.IReadSequence):
    """List of the <division>s of an zeit.content.article.interfaces.IArticle
    """


class IPage(zope.interface.Interface):
    """A page offers list-access to the blocks
    (zeit.edit.interfaces.IBlock) contained in it.
    """

    number = zope.interface.Attribute(
        'The position of this division in the article body (0-based)')
    teaser = zope.interface.Attribute('Page teaser')

    def __iter__(self):
        """iterate over our blocks"""


class ITeaserImage(zope.interface.Interface):
    """ A Teaser Image """


