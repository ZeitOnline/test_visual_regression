import grokcore.component
import pyramid.httpexceptions

import zeit.campus.interfaces
import zeit.cms.interfaces

import zeit.web
import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.security
import zeit.web.core.view
import zeit.web.campus.navigation


DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.campus.interfaces.IZCOContent)
def campus_topiclink(context):

    def get_default_topics():
        context = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/campus/index', None)
        return zeit.web.core.centerpage.TopicLink(context)

    return DEFAULT_TERM_CACHE.get_or_create(
        'campus-default-topics',
        get_default_topics,
        should_cache_fn=bool)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Campus ONLINE | studieren. arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Campus'

    # make job market links available in view
    jobmarket = zeit.web.campus.navigation.JOB_MARKET_SOURCE

    # make toolbox links available in view
    toolbox = zeit.web.campus.navigation.TOOL_SOURCE

    # make flyout links available in view
    flyoutnavi = zeit.web.campus.navigation.TOOL_FLYOUT_SOURCE

    @zeit.web.reify
    def adwords(self):
        return ['zeitonline', 'zeitcampus']

    @zeit.web.reify
    def adcontroller_handle(self):
        suffix = '_trsf'
        replacements = {
            'article': 'artikel',
            'gallery': 'galerie'}
        if self.is_hp:
            return 'campus_homepage{}'.format(suffix)
        if self.is_advertorial:
            return '{}_{}{}'.format(
                'mcs' if 'mcs/' in self.banner_channel else 'adv',
                'index' if self.type == 'centerpage' else 'artikel',
                suffix)
        if self.type == 'centerpage':
            return 'index{}'.format(suffix)
        if self.type in replacements:
            return '{}{}'.format(replacements[self.type], suffix)
        return 'centerpage{}'.format(suffix)

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT Campus'

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitcampus'

    @zeit.web.reify
    def ressort_literally(self):
        return 'Campus'

    @zeit.web.reify
    def topic_page(self):
        try:
            return zeit.campus.interfaces.ITopic(self.context).page
        except TypeError:
            return None

    @zeit.web.reify
    def topic_label(self):
        try:
            topic = zeit.campus.interfaces.ITopic(self.context)
        except TypeError:
            return ''
        if topic.label:
            return topic.label
        return getattr(topic.page, 'title', '')


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=campus',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)


@zeit.web.view_config(
    route_name='campus_framebuilder',
    renderer='templates/framebuilder/framebuilder.html')
class FrameBuilder(zeit.web.core.view.FrameBuilder, Base):

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/campus/index')
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()


class Content(Base):

    @zeit.web.reify
    def article_layout(self):
        return 'default'
