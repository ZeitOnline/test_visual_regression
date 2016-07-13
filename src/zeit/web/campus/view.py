import re

import pyramid.view

import zeit.campus.interfaces

import zeit.web.core.application
import zeit.web.core.security
import zeit.web.core.view
import zeit.web.campus.module.toolbox


def is_zco_content(context, request):
    toggle = zeit.web.core.application.FEATURE_TOGGLES.find('campus_launch')
    return toggle and zeit.campus.interfaces.IZCOContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Campus ONLINE | studieren. arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Campus'

    # make toolbox links available in view
    toolbox = zeit.web.campus.module.toolbox.TOOL_SOURCE

    @zeit.web.reify
    def adwords(self):
        return ['zeitonline', 'zeitcampus']

    @zeit.web.reify
    def banner_channel(self):
        # manually banner_id rules first
        if self.context.banner_id is not None:
            return u'{}/{}'.format(self.context.banner_id, self.banner_type)
        # special handling for advertorials
        if self.ressort == 'angebote':
            adv_title = self.context.advertisement_title or self.ressort
            return u'{}/{}/{}'.format(
                'campus',
                'angebote',
                "".join(re.findall(r"[A-Za-z0-9_]*", adv_title)).lower())
        # the big rest, for now
        topiclabel = getattr(self, 'topic_label', '')
        topiclabel = zeit.web.core.template.format_iqd(topiclabel)
        return u'{}/{}/{}'.format(
            'campus',
            'thema' if topiclabel else '',
            topiclabel or '')


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
            self.context.advertising_enabled = self.banner_on
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
