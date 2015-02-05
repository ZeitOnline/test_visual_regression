import zeit.magazin.interfaces
import zeit.web.core.view


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'


class Base(zeit.web.core.view.Base):

    _navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo',
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2',
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3',
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4',
        )
    }

    @zeit.web.reify
    def breadcrumb(self):
        crumb = self._navigation
        l = [crumb['start']]
        l.append(crumb['zmo'])
        if self.context.ressort in crumb:
            l.append(crumb[self.context.ressort])
        if self.context.sub_ressort in crumb:
            l.append(crumb[self.context.sub_ressort])
        if self.title:
            l.append((self.title, ''))
        return l

    @zeit.web.reify
    def pagetitle(self):
        suffix = ''
        if self.is_hp is False:
            suffix = ' | ZEITmagazin'
        try:
            seo = zeit.seo.interfaces.ISEO(self.context)
            if seo.html_title:
                return seo.html_title + suffix
        except TypeError:
            pass
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        tokens = (self.supertitle, self.title)
        return ': '.join([t for t in tokens if t]) + suffix or default

    @zeit.web.reify
    def pagedescription(self):
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        try:
            seo = zeit.seo.interfaces.ISEO(self.context)
        except TypeError:
            return default
        if seo.html_description:
            return seo.html_description
        if self.context.subtitle:
            return self.context.subtitle
        return default

    def banner_toggles(self, name):
        # no banner toggles in ZMO in the moment
        return True
