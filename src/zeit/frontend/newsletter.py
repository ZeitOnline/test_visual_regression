from babel.dates import get_timezone
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.frontend.block import IFrontendBlock
import zeit.frontend.view
import zeit.newsletter.interfaces


@view_config(context=zeit.newsletter.interfaces.INewsletter,
             renderer='dav://newsletter.html')
class Newsletter(zeit.frontend.view.Base):

    def translate_url(self, url):
        return url.replace('http://xml.zeit.de/', 'http://www.zeit.de/', 1)

    def image_url(self, url):
        return url.replace('http://xml.zeit.de/', 'http://images.zeit.de/', 1)

    @property
    def date_first_released(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @property
    def body(self):
        return [IFrontendBlock(x) for x in self.context.body.values()]
