import pyramid.view

import zeit.cms.workflow.interfaces
import zeit.newsletter.interfaces

import zeit.web.core.block
import zeit.web.core.view


@pyramid.view.view_config(context=zeit.newsletter.interfaces.INewsletter,
                          renderer='dav://newsletter.html')
@pyramid.view.view_config(context=zeit.newsletter.interfaces.INewsletter,
                          request_param='format=txt',
                          renderer='dav://newsletter_text.html')
class Newsletter(zeit.web.core.view.Base):

    def __call__(self):
        if self.request.params.get('format') == 'txt':
            self.request.response.content_type = 'text/plain; charset=utf-8'
        return {}

    @property
    def body(self):
        return [zeit.web.core.interfaces.IFrontendBlock(x) for x in
                self.context.body.values()]
