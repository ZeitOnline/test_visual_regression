import pyramid.view

import zeit.campus.interfaces

import zeit.web.core.application
import zeit.web.core.security
import zeit.web.core.view


def is_zco_content(context, request):
    toggle = zeit.web.core.application.FEATURE_TOGGLES.find('campus_launch')
    return toggle and zeit.campus.interfaces.IZCOContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Campus ONLINE | studieren. arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Campus'

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore.
        """
        keywords = ','.join(self.adwords)

        topiclabel = getattr(self, 'topic_label', '')
        topiclabel = zeit.web.core.template.format_iqd(topiclabel)

        return [('$handle', self.adcontroller_handle),
                ('level2', 'campus'),
                ('level3', 'thema' if topiclabel else ''),
                ('level4', topiclabel or ''),
                ('$autoSizeFrames', True),
                ('keywords', keywords),
                ('tma', '')]


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

    @zeit.web.reify
    def adcontroller_values(self):

        banner_channel = self.request.GET.get('banner_channel', None)

        if not banner_channel:
            return

        adc_levels = banner_channel.split('/')

        return [('$handle', adc_levels[3] if len(adc_levels) > 3 else ''),
                ('level2', adc_levels[0] if len(adc_levels) > 0 else ''),
                ('level3', adc_levels[1] if len(adc_levels) > 1 else ''),
                ('level4', adc_levels[2] if len(adc_levels) > 2 else ''),
                ('$autoSizeFrames', True),
                ('keywords', adc_levels[4] if len(adc_levels) > 4 else ''),
                ('tma', '')]


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
