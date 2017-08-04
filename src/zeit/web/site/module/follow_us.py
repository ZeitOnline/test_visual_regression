import zope.component

import zeit.content.image.interfaces

import zeit.web.core.image
import zeit.web.site.area.rss
import zeit.web.core.centerpage


@zeit.web.register_module('follow_us')
class FollowUs(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def buttons(self):
        return [
            ('facebook', 'https://www.facebook.com/zeitonline/', 'Facebook',
                'Folgen Sie uns auf Facebook'),
            ('twitter', 'https://twitter.com/zeitonline', 'Twitter',
                'Folgen Sie uns bei Twitter'),
            ('instagram', 'https://www.instagram.com/zeit/', 'Instagram',
                'Folgen Sie uns bei Instagram'),
            ('xing', 'https://www.xing.com/news/pages/zeit-online-165', 'Xing',
                'Abonnieren Sie uns bei Xing'),
            ('newsletter', 'http://community.zeit.de/newsletter', 'Newsletter',
                'Abonnieren Sie unseren Newsletter')]
