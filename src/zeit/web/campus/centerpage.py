import grokcore.component

import zeit.campus.interfaces

import zeit.web.core.cache
import zeit.web.core.centerpage
import zeit.web.core.interfaces


DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.campus.interfaces.IZCOContent)
def campus_topiclink(context):
    topiclink = zeit.web.core.centerpage.TopicLink(context)
    if topiclink:
        return topiclink

    def get_default_topics():
        context = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/campus/index', None)
        return zeit.web.core.centerpage.TopicLink(context)

    return DEFAULT_TERM_CACHE.get_or_create(
        'campus-default-topics',
        get_default_topics,
        should_cache_fn=bool)
