import pyramid.interfaces
import zope.interface

import zeit.edit.interfaces


class IArticleModule(zope.interface.Interface):
    """An item that provides data from an article-body module to a Jinja macro.

    This interface is both a marker for identifying front-end objects
    representing modules, and a mechanical detail of using the ZCA to construct
    such a front-end representation of a given vivi article-body modules.
    """

    layout = zope.interface.Attribute(
        'String that modifies how this block is to be displayed')

    context = zope.interface.Attribute('The vivi-side module object')


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


class ICachingTime(zope.interface.Interface):
    """Provides a client caching time in seconds for a content object such as
    ICMSContent.
    """


class IVarnishCachingTime(zope.interface.Interface):
    """Provides a caching time in seconds for a content object such as
    ICMSContent for our varnish cache.
    """


class INewsfeed(zope.interface.Interface):
    """Marker interface to make ICachingTime for newsfeed.zeit.de separately
    configurable."""


class IExpiration(zope.interface.Interface):

    seconds = zope.interface.Attribute(
        'The number of seconds relative to now when the content object '
        ' will no longer be published')

    is_expired = zope.interface.Attribute('boolean')


class IPage(zope.interface.Interface):
    """A page offers list-access to the blocks (zeit.edit.interfaces.IBlock)
    contained in it.
    """

    number = zope.interface.Attribute(
        'The position of this division in the article body (0-based)')
    teaser = zope.interface.Attribute('Page teaser')

    def __iter__():
        """Iterate over our blocks"""


class IImage(zope.interface.Interface):
    """A universal interface for zeit.web images"""

    alt = zope.interface.Attribute('Alt title of the image')
    caption = zope.interface.Attribute('Caption of the image')
    copyrights = zope.interface.Attribute('Copyrights of the image')
    fill_color = zope.interface.Attribute('Effective background fill color')
    group = zope.interface.Attribute('Imagegroup the image is based on')
    href = zope.interface.Attribute('Href attribute of the image')
    path = zope.interface.Attribute('Absolute path to the image')
    fallback_path = zope.interface.Attribute('Sized fallback path')
    fallback_height = zope.interface.Attribute('Sized height of the variant')
    fallback_width = zope.interface.Attribute('Sized width of the variant')
    ratio = zope.interface.Attribute('Ratio of the image variant')
    title = zope.interface.Attribute('Title of the image')
    variant_id = zope.interface.Attribute('Pattern or variant ID')


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


class INextread(IArticleModule):
    """Nextread teaser block must be similar to zeit.content.cp.TeaserBlock"""


class ISettings(pyramid.interfaces.ISettings):
    """Dictionary of application configuration settings.

    Settings come from two sources.
    1. The web.ini file ("deployment settings"), read once on process startup.
    2. An XML file read from a URL ("runtime settings"), read on demand and
    cached using the cache region `config`.

    Read operations look in the deployment settings first, then runtime.
    Write operations write to the deployment settings.
    """


class ITopicLink(zope.interface.Interface):
    """TopicLink sanitizer"""


class IInternalUse(zope.interface.Interface):
    """Marker interface for ICMSContent, so Source entries can be ``available``
    only for zeit.web, but not vivi.
    """


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

    def get_comments():
        """Retrieve a ranking of most commented articles"""

    def get_score():
        """Return a ranking of highest buzz-scoring articles"""

    def get_trend():
        """Return a ranking of highest buzz-trending articles"""

    def get_social():
        """Get a ranking of articles trending on social platforms"""

    def get_views():
        """Output a ranking of articles with top view counts"""

    def get_buzz():
        """Collect a buzz summary for an article by uniqueId"""


class IReachData(zope.interface.Interface):
    """Adapts an article returned by IReach to access its score value"""

    score = zope.interface.Attribute('reach score')


class IPodigee(zope.interface.Interface):

    def get_episode(episode_id):
        """Returns a dict with episode metadata. If an error occurs, returns an
        empty dict, but will always contain a key `podcast_id` for use with
        `get_podcast`.
        """

    def get_podcast(podcast_id):
        """Returns a dict with podcast metadata. If an error occurs, returns an
        empty dict."""


class IMail(zope.interface.Interface):

    def send(from_, to, subject, body):
        """Sends an email."""


class ICaptcha(zope.interface.Interface):

    def verify(captcha_response, nojs):
        """Returns True if captcha is valid."""


class IMetrics(zope.interface.Interface):

    def time(identifier):
        """Context manager that collects timing information.
        Pass a full dotted name as identifier.

        Also available via convenience shortcut ``zeit.web.metrics.timer``.

        Example:
        with zeit.web.metrics.timer('zeit.web.core.template.something'):
            # do things
        """

    def increment(identifier, delta=1):
        """Increments the given counter."""

    def set_gauge(identifier, value):
        """Sets a gauge value."""

    # low-level access for more involved operations.

    def timer(identifier=None):
        """Returns a ``statsd.Timer``."""

    def counter(identifier=None):
        """Returns a ``statsd.Counter``."""

    def gauge(identifier=None):
        """Returns a ``statsd.Gauge``."""


class IPagination(zope.interface.Interface):
    """An pagination object to render a page with a certain subset of an
       resultset (e.g solr query). Also used to display html pagination
       object."""

    page = zope.interface.Attribute(
        'The actual page being displayed.')
    current_page = zope.interface.Attribute(
        'Same as page. Kept for hysterical raisins.')
    total_pages = zope.interface.Attribute(
        'Number of pages available.')
    pagination = zope.interface.Attribute('A list of page numbers.')
    pagination_info = zope.interface.Attribute(
        'Some metada, such as label for pages or buttons in the pagination')

    def page_info(page_nr):
        """Get information of the page items in the pagination object."""


class IDetailedContentType(zope.interface.Interface):
    """Returns more detailed content type information, not just
    article/centerpage/etc. but also the CP-Type or Article-Template etc.

    The format is a dotted string, e.g. 'centerpage.autotopic.person'.
    """


class ICommunity(zope.interface.Interface):
    """Represents the comment system."""

    def get_thread(unique_id, sort='asc', page=0,
                   cid=None, parent_cid=None, local_offset=0):
        pass

    def get_comment(unique_id, cid):
        pass

    def get_comment_count(unique_id):
        pass

    def get_comment_counts(*unique_ids):
        pass

    def get_user_comments(author, page=1, rows=6, sort='DESC'):
        pass

    def is_healthy():
        pass


class ILiveblogInfo(zope.interface.Interface):
    """Returns liveblog metadata."""


class IExternalTemporaryImage(zope.interface.Interface):
    """A marker interface to distinguish externally hosted images vs. those
    from friedbert itself."""


class IPaywallAccess(zope.interface.Interface):
    """ Get access state of a resource"""


class IVertical(zope.interface.Interface):
    """Returns short identifier string (zon/zmo/zco/zar) to signify which
    vertical an ICMSContent belongs to.

    This is not quite the same as which zeit.cms.section.ISectionMarker the
    content has, since we have to handle some additional special cases.
    """


class IContentMarkerInterfaces(zope.interface.Interface):
    """Returns a list of marker interfaces that are added to ICMSContent
    objects.
    """


class ISeries(zope.interface.Interface):
    """A interface for zeit.web series"""

    def series_kind():
        """Returns the kind of a series (e.g. podcast)"""

    def series_title():
        """Returns the title of a series"""

    def series_url():
        """Returns the url of a series"""
