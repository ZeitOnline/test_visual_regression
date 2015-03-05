import pyramid.interfaces
import zope.interface
import zope.interface.common.sequence


class IDeltaTime(zope.interface.Interface):
    """A date that has been processed through babel which is actually used
    for delta time representations.
    """

    days = zope.interface.Attribute(
        'A delta days entity')
    hours = zope.interface.Attribute(
        'A delta hours entity')
    minutes = zope.interface.Attribute(
        'A delta minutes entity')


class IDeltaTimeEntity(zope.interface.Interface):
    """An entity of a babelfied date from a delta time"""

    delta = zope.interface.Attribute(
        'A delta time as base for delta time derivates')
    number = zope.interface.Attribute(
        'An integer representation of a delta time')
    text = zope.interface.Attribute(
        'A text representation of a delta time')


class IDeltaDaysEntity(IDeltaTimeEntity):
    """A babelfied days entity from a delta time"""


class IDeltaHoursEntity(IDeltaTimeEntity):
    """A babelfied hours entity from a delta time"""


class IDeltaMinutesEntity(IDeltaTimeEntity):
    """An babelfied minutes entity from a delta time"""


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
        """Iterate over our blocks"""


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


class ISettings(pyramid.interfaces.ISettings):
    """Custom interface class to register settings as a utility"""


class IImageScales(zope.interface.Interface):
    """Image scale utility factory"""


class ITeaserMapping(zope.interface.Interface):
    """Legacy teaser mapping"""


class ITopicLink(zope.interface.Interface):
    """TopicLink sanitizer"""


class IInternalUse(zope.interface.Interface):
    """Marks internally used source entries"""
