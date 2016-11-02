import pyramid.view

import zeit.campus.interfaces

import zeit.web.core.application
import zeit.web.core.security
import zeit.web.core.view
import zeit.web.campus.module.toolbox


def is_zco_content(context, request):
    return zeit.campus.interfaces.IZCOContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Campus ONLINE | studieren. arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Campus'

    # make toolbox links available in view
    toolbox = zeit.web.campus.module.toolbox.TOOL_SOURCE

    @zeit.web.reify
    def adwords(self):
        return ['zeitonline', 'zeitcampus']

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT Campus'

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitcampus'


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=campus',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)


@pyramid.view.view_config(
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

    @zeit.web.reify
    def article_layout(self):
        return 'default'
