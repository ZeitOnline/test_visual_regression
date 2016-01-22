import logging

import zope.component

import zeit.web.core.interfaces
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('quiz')
class Quiz(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def title(self):
        return self.context.title

    @zeit.web.reify
    def url(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('quiz_url', '').format(quiz_id=self.context.quiz_id)
