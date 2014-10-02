import zope.interface
import zope.interface.common.sequence


class INavigation(zope.interface.Interface):
    """A navigation bar containing navigation items"""

    navigation_items = zope.interface.Attribute('navigation_items')


class INavigationItem(zope.interface.Interface):
    """Navigation items linking to different sections and sub sections"""

    href = zope.interface.Attribute('href')
    item_id = zope.interface.Attribute('item_id')
    navigation_items = zope.interface.Attribute('navigation_items')
    text = zope.interface.Attribute('text')


class IPages(zope.interface.common.sequence.IReadSequence):
    """List of the <division>s of an zeit.content.article.interfaces.IArticle
    """


class IPage(zope.interface.Interface):
    """A page offers list-access to the blocks (zeit.edit.interfaces.IBlock)
    contained in it.
    """

    number = zope.interface.Attribute(
        'The position of this division in the article body (0-based)')
    teaser = zope.interface.Attribute('Page teaser')

    def __iter__(self):
        """iterate over our blocks"""


class ITeaserImage(zope.interface.Interface):
    """A Teaser Image"""


class IPlace(zope.interface.Interface):
    """A place is a space on the website, which can be filled with a banner.
    """


class IIqdMobileList(zope.interface.Interface):
    """A set of iqd ids for a certain ressort.
    """


class IBannerlist(zope.interface.Interface):
    """A list of ad places"""


class INextreadTeaserBlock(zope.interface.Interface):
    """Nextread teaser block must be similar to zeit.content.cp.TeaserBlock"""


class ITeaser(zope.interface.Interface):

    image = zope.interface.Attribute('image')
    gallery = zope.interface.Attribute('gallery')
    video = zope.interface.Attribute('video')
    context = zope.interface.Attribute('context')


class ITeaserSequence(zope.interface.Interface):

    context = zope.interface.Attribute('context')
    sequence = zope.interface.Attribute('sequence')
    refs = zope.interface.Attribute('refs')
