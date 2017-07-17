import zeit.arbeit.interfaces
import zeit.web
import zeit.web.core.application
import zeit.web.core.view


def is_zar_content(context, request):
    return zeit.web.core.application.FEATURE_TOGGLES.find(
        'arbeit') and zeit.arbeit.interfaces.IZARContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Arbeit ONLINE | arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Arbeit'


class Content(Base):

    @zeit.web.reify
    def article_layout(self):
        return 'default'


@zeit.web.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=arbeit',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)
