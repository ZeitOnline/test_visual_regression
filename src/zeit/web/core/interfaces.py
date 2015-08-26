import pyramid.interfaces
import zope.interface
import zope.interface.common.sequence

import zeit.edit.interfaces


class IFrontendBlock(zope.interface.Interface):
    """An item that provides data from an article-body block to a Jinja macro.

    This interface is both a marker for identifying front-end objects
    representing blocks, and a mechanical detail of using the ZCA to construct
    such a front-end representation of a given vivi article-body block.
    """


class IFrontendHeaderBlock(zope.interface.Interface):
    """A HeaderBlock identifies elements that appear only in headers of
    the content.
    """


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
    seconds = zope.interface.Attribute(
        'A delta seconds entity')


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
    """A babelfied minutes entity from a delta time"""


class IDeltaSecondsEntity(IDeltaTimeEntity):
    """A babelfied seconds entity from a delta time"""


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


class IContentAdBlock(zope.interface.Interface):
    """A space for an iqd content ad"""


class IIqdMobileList(zope.interface.Interface):
    """A set of iqd ids for a certain ressort.
    """


class IBannerlist(zope.interface.Interface):
    """A list of ad places"""


class INextread(IFrontendBlock):
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


class IBreakingNews(zope.interface.Interface):
    """Breaking news"""

    date_last_published = zope.interface.Attribute(
        'Publish date of breaking news')
    doc_path = zope.interface.Attribute(
        'Document path of breaking news article')
    publish_string = zope.interface.Attribute(
        'Publish date of breaking news as string')
    title = zope.interface.Attribute('title')
    uniqueId = zope.interface.Attribute(
        'UniqueId of breaking news')


class ITraversable(zope.interface.Interface):
    """Content types that modify the traversal dictionary"""


class IBlock(zeit.edit.interfaces.IBlock):
    """Interface for zeit.web specific IBlock implementations"""


class IReach(zope.interface.Interface):

    def get_comments(self):
        """Retrieve a ranking of most commented articles"""

    def get_score(self):
        """Return a ranking of highest buzz-scoring articles"""

    def get_social(self):
        """Get a ranking of articles trending on social platforms"""

    def get_views(self):
        """Output a ranking of articles with top view counts"""

    def get_buzz(self):
        """Collect a buzz summary for an article by uniqueId"""


class IMetrics(zope.interface.Interface):

    def time(self, identifier):
        """Context manager that collects timing information.
        Pass a full dotted name as identifier.

        Also available via convenience shortcut ``zeit.web.metrics.timer``.

        Example:
        with zeit.web.metrics.timer('zeit.web.core.template.something'):
            # do things
        """

    def increment(self, identifier, delta=1):
        """Increments the given counter."""

    def set_gauge(self, identifier, value):
        """Sets a gauge value."""

    # low-level access for more involved operations.

    def timer(self, identifier=None):
        """Returns a ``statsd.Timer``."""

    def counter(self, identifier=None):
        """Returns a ``statsd.Counter``."""

    def gauge(self, identifier=None):
        """Returns a ``statsd.Gauge``."""
