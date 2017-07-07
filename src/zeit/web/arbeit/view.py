import zeit.campus.interfaces
import zeit.cms.interfaces

import zeit.web
import zeit.web.core.application
import zeit.web.core.cache
import zeit.web.core.interfaces
import zeit.web.core.security
import zeit.web.core.view


def is_zar_content(context, request):
    return zeit.web.core.application.FEATURE_TOGGLES.find(
        'arbeit') and request.path.startswith('/arbeit/')


class Base(zeit.web.core.view.Base):

    seo_title_default = u'ZEIT Arbeit ONLINE | arbeiten. leben.'
    pagetitle_suffix = u' | ZEIT Arbeit'


class Content(Base):

    @zeit.web.reify
    def article_layout(self):
        return 'default'
