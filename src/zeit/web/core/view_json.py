import pyramid.response
import zope.component

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.date
import zeit.web.core.interfaces
import zeit.web.core.navigation
import zeit.web.site.view_centerpage

# Please keep doc/api.raml up to date if you change an interface (ND)


@zeit.web.view_config(
    route_name='json_delta_time',
    renderer='jsonp')
def json_delta_time(request):
    unique_id = request.GET.get('unique_id', None)
    date = request.GET.get('date', None)
    base_date = request.GET.get('base_date', None)
    parsed_base_date = zeit.web.core.date.parse_date(base_date)
    if unique_id is not None:
        return json_delta_time_from_unique_id(
            request, unique_id, parsed_base_date)
    elif date is not None:
        return json_delta_time_from_date(date, parsed_base_date)
    else:
        return pyramid.response.Response(
            'Missing parameter: unique_id or date', 412)


def json_delta_time_from_date(date, parsed_base_date):
    parsed_date = zeit.web.core.date.parse_date(date)
    if parsed_date is None:
        return pyramid.response.Response(
            'Invalid parameter: date', 412)
    dt = zeit.web.core.date.DeltaTime(parsed_date, parsed_base_date)
    return {'delta_time': {'time': dt.get_time_since_modification()}}


def json_delta_time_from_unique_id(request, unique_id, parsed_base_date):
    try:
        content = zeit.cms.interfaces.ICMSContent(unique_id)
        assert zeit.content.cp.interfaces.ICenterPage.providedBy(content)
    except (TypeError, AssertionError):
        return pyramid.response.Response('Invalid resource', 400)
    delta_time = {}
    for article in zeit.web.site.view_centerpage.Centerpage(content, request):
        time = zeit.web.core.date.get_delta_time_from_article(
            article, base_date=parsed_base_date)
        if time:
            delta_time[article.uniqueId] = time
    return {'delta_time': delta_time}


@zeit.web.view_config(
    route_name='json_comment_count',
    renderer='jsonp')
def json_comment_count(request):
    try:
        unique_id = request.GET.get('unique_id', None)
    except UnicodeDecodeError:
        unique_id = None
    if unique_id is None:
        return pyramid.response.Response(
            'Missing value for parameter: unique_id', 412)

    try:
        context = zeit.cms.interfaces.ICMSContent(unique_id)
    except TypeError:
        return pyramid.response.Response(
            'Invalid value for parameter: unique_id', 412)

    if zeit.content.cp.interfaces.ICenterPage.providedBy(context):
        articles = list(
            zeit.web.site.view_centerpage.Centerpage(context, request))
    else:
        article = zeit.content.article.interfaces.IArticle(context, None)
        articles = [article] if article is not None else []

    community = zope.component.getUtility(zeit.web.core.interfaces.ICommunity)
    counts = community.get_comment_counts(*[a.uniqueId for a in articles])
    comment_count = {}

    for article in articles:
        count = counts.get(article.uniqueId, 0)
        comment_count[article.uniqueId] = '%s Kommentar%s' % (
            count == 0 and 'Keine' or count, count != '1' and 'e' or '')

    return {'comment_count': comment_count}


@zeit.web.view_config(
    route_name='json_update_time',
    renderer='jsonp')
def json_update_time(request):
    try:
        resource = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/{}'.format(
                request.matchdict['path']), None)
        if resource is None:
            resource = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/{}'.format(request.matchdict['path']))

        info = zeit.cms.workflow.interfaces.IPublishInfo(resource)
        dlps = info.date_last_published_semantic.isoformat()
        dlp = info.date_last_published.isoformat()

    except (AttributeError, KeyError, TypeError):
        dlps = dlp = None
    request.response.cache_expires(5)
    return {'last_published': dlp, 'last_published_semantic': dlps}


@zeit.web.view_config(
    route_name='json_topic_config',
    renderer='jsonp')
def json_topic_config(request):
    try:
        resource = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index')
        cp = zeit.content.cp.interfaces.ICenterPage(resource)
        config = {'topics': []}
        for x in xrange(1, 4):
            label = getattr(cp, 'topiclink_label_{}'.format(x))
            url = getattr(cp, 'topiclink_url_{}'.format(x))
            if url and label:
                config['topics'].append({'topic': label, 'url': url})
    except (AttributeError, KeyError, TypeError):
        config = {}
    request.response.cache_expires(5)
    return config
