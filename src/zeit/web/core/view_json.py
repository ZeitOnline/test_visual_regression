import pyramid.response
import uuid as uuidlib
import zope.component

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.retresco.interfaces

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
    ids = [a.uniqueId for a in articles
           if getattr(a, 'commentsAllowed', False)]
    counts = community.get_comment_counts(*ids) if ids else {}
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


@zeit.web.view_config(
    route_name='json_article_query',
    request_method='POST',
    renderer='jsonp')
def json_article_query(request):
    try:
        assert isinstance(request.json_body, dict), 'body must be an object'
        uuids = request.json_body.get('uuids', [])
        unique_ids = request.json_body.get('uniqueIds', [])
        assert isinstance(uuids, list), 'uuids must be a list'
        assert isinstance(unique_ids, list), 'uniqueIds must be a list'
        assert len(uuids) <= 1000, "can't handle more than 1000 uuids"
        assert len(unique_ids) <= 1000, "can't handle more than 1000 uniqueIds"
    except AssertionError, e:
        raise pyramid.httpexceptions.HTTPBadRequest(e.message)

    if not uuids and not unique_ids:
        return []

    lead_unique_id = None
    hp_unique_ids = []
    hp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index', None)
    if hp:
        # For performance, we only check against the first five regions (ND)
        for region in hp.values()[:5]:
            for area in region.values():
                teasered = list(
                    zeit.content.cp.interfaces.ITeaseredContent(area))
                if not lead_unique_id and len(teasered):
                    lead_unique_id = teasered[0].uniqueId
                hp_unique_ids.extend(t.uniqueId for t in teasered)

    try:
        for unique_id in unique_ids:
            assert isinstance(
                unique_id, basestring), 'unique_id must be string'
            assert unique_id.startswith(zeit.cms.interfaces.ID_NAMESPACE), (
                'invalid uniqueId: %s' % unique_id)
        for index, uuid in enumerate(uuids):
            try:
                uuids[index] = '{%s}' % uuidlib.UUID(uuid).urn
            except:
                raise AssertionError('invalid uuid: %s' % uuid)
    except AssertionError, e:
        raise pyramid.httpexceptions.HTTPBadRequest(e.message)

    if zeit.web.core.application.FEATURE_TOGGLES.find('elasticsearch_zoca'):
        results = _get_articles_elasticsearch(unique_ids, uuids)
    else:
        results = _get_articles_solr(unique_ids, uuids)

    for item in results:
        item['lead_article'] = item['uniqueId'] == lead_unique_id
        item['on_homepage'] = item['uniqueId'] in hp_unique_ids
        item['url'] = item['uniqueId'].replace(
            zeit.cms.interfaces.ID_NAMESPACE, request.route_url('home'))
    return results


def _get_articles_solr(unique_ids=[], uuids=[]):
    terms = [
        'uniqueId:"%s"' % i for i in unique_ids] + [
        'uuid:"%s"' % i for i in uuids]
    query = zeit.solr.query.or_(*terms)
    filter_query = zeit.solr.query.field_raw('comments', 'true')
    fields = ','.join((
        'uuid',
        'uniqueId',
        'supertitle',
        'title',
        'teaser_text',
        'ressort',
        'sub_ressort',
        'date_first_released',
        'date_last_published',
        'keywords'))
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    with zeit.web.core.metrics.timer('zoca.solr.reponse_time'):
        results = solr.search(
            query,
            rows=1000,
            fl=fields,
            sort='date_first_released desc',
            fq=filter_query)
    return list(results)


def _get_articles_elasticsearch(unique_ids=[], uuids=[]):
    elasticsearch = zope.component.getUtility(
        zeit.retresco.interfaces.IElasticsearch)
    urls = [
        i.replace(zeit.cms.interfaces.ID_NAMESPACE, '/') for i in unique_ids]
    query = {
        'query': {
            'bool': {
                'minimum_should_match': 1,
                'should': [
                    {'terms': {'doc_id': uuids}},
                    {'terms': {'url': urls}}],
                'filter': {'term': {'payload.document.comments': True}}
            }
        },
        '_source': [
            'doc_id',
            'url',
            'supertitle',
            'title',
            'teaser',
            'payload.document.ressort',
            'payload.document.sub_ressort',
            'payload.document.date_first_released',
            'payload.document.comments_premoderate',
            'payload.workflow.date_last_published',
            'rtr_tags'
        ]
    }
    with zeit.web.core.metrics.timer('zoca.elasticsearch.reponse_time'):
        results = elasticsearch.search(
            query,
            'payload.document.date_first_released:desc',
            rows=1000)
    for item in results:
        payload = item.pop('payload', {})
        workflow = payload.get('workflow', {})
        doc = payload.get('document', {})
        path = item.pop('url', u'').lstrip(u'/')
        item['uniqueId'] = u''.join((zeit.cms.interfaces.ID_NAMESPACE, path))
        item['uuid'] = item.pop('doc_id')
        item['teaser_text'] = item.pop('teaser', None)
        item['keywords'] = item.pop('rtr_tags', [])
        item['date_last_published'] = workflow.get('date_last_published')
        item['ressort'] = doc.get('ressort')
        item['sub_ressort'] = doc.get('sub_ressort')
        item['date_first_released'] = doc.get('date_first_released')
        item['comments_premoderate'] = doc.get('comments_premoderate', False)
    return list(results)


@zeit.web.view_config(
    route_name='json_ressort_list',
    renderer='jsonp')
def json_ressort_list(request):
    ressort_list = []
    for item in zeit.web.core.navigation.NAVIGATION_SOURCE.navigation.values():
        if item.label and 'Anzeige' in item.label:
            continue
        ressort_list.append({
            'name': zeit.cms.content.sources.unicode_or_none(item.text),
            'uniqueId': zeit.cms.content.sources.unicode_or_none(item.href)
        })
    return ressort_list
