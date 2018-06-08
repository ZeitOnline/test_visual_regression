import grokcore.component
import zeit.arbeit.interfaces
import zeit.web
import zeit.web.core.cache
import zeit.web.core.application
import zeit.web.core.interfaces
import zeit.web.core.view

DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.arbeit.interfaces.IZARContent)
def arbeit_topiclink(context):

    def get_topics_from_cp():
        context = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/arbeit/index', None)
        return zeit.web.core.centerpage.TopicLink(context)

    return DEFAULT_TERM_CACHE.get_or_create(
        'arbeit-default-topics',
        get_topics_from_cp,
        should_cache_fn=bool)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Arbeit ONLINE | arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Arbeit'

    @zeit.web.reify
    def ressort_literally(self):
        return 'Arbeit'

    @zeit.web.reify
    def adwords(self):
        return ['zeitonline', 'zeitarbeit']

    @zeit.web.reify
    def adcontroller_handle(self):
        suffix = '_trsf'
        replacements = {
            'article': 'artikel',
            'gallery': 'galerie'}
        if self.is_hp:
            return 'arbeit_homepage{}'.format(suffix)
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


class Content(Base):
    pass


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=arbeit',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)
