from babel.dates import get_timezone
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.web.core.block import IFrontendBlock
import zeit.web.core.view
import zeit.newsletter.interfaces


@view_config(context=zeit.newsletter.interfaces.INewsletter,
             renderer='dav://newsletter.html')
@view_config(context=zeit.newsletter.interfaces.INewsletter,
             request_param='format=txt',
             renderer='dav://newsletter_text.html')
class Newsletter(zeit.web.core.view.Base):

    def __call__(self):
        if self.request.params.get('format') == 'txt':
            self.request.response.content_type = 'text/plain; charset=utf-8'
        return {}

    @property
    def date_first_released(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @property
    def body(self):
        return [IFrontendBlock(x) for x in self.context.body.values()]
