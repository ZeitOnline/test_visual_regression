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
            ('flipboard', 'https://flipboard.com/@ZEITONLINE', 'Flipboard',
                'Folgen Sie uns bei Flipboard'),
            ('xing', 'https://www.xing.com/news/pages/zeit-online-165', 'Xing',
                'Abonnieren Sie uns bei Xing')]


@zeit.web.register_module('zmo_follow_us')
class ZMOFollowUs(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def buttons(self):
        return [
            ('twitter', 'https://twitter.com/zeitmagazin?lang=de', 'Twitter',
                'Folgen Sie uns bei Twitter'),
            ('instagram', 'https://www.instagram.com/zeitmagazin/',
                'Instagram', 'Folgen Sie uns bei Instagram'),
            ('facebook', 'https://de-de.facebook.com/ZEITmagazin/', 'Facebook',
                'Folgen Sie uns auf Facebook')]
