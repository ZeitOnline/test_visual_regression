import zeit.magazin.interfaces
import zeit.web.core.view


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'


class Base(zeit.web.core.view.Base):

    @zeit.web.reify
    def breadcrumb(self):
        crumbs = {
            'start': (
                'Start',
                'http://{}/index'.format(self.request.host),
                'myid1'
            ),
            'zmo': (
                'ZEIT Magazin',
                'http://{}/zeit-magazin/index'.format(self.request.host),
                'myid_zmo',
            ),
            'leben': (
                'Leben',
                'http://{}/zeit-magazin/leben/index'.format(self.request.host),
                'myid2',
            ),
            'mode-design': (
                'Mode & Design',
                'http://{}/zeit-magazin/mode-design/index'.format(
                    self.request.host),
                'myid3',
            ),
            'essen-trinken': (
                'Essen & Trinken',
                'http://{}/zeit-magazin/essen-trinken/index'.format(
                    self.request.host),
                'myid4',
            )
        }
        crumb_list = [crumbs['start']]
        crumb_list.append(crumbs['zmo'])
        if self.context.ressort in crumbs:
            crumb_list.append(crumbs[self.context.ressort])
        if self.context.sub_ressort in crumbs:
            crumb_list.append(crumbs[self.context.sub_ressort])
        if self.title:
            crumb_list.append((self.title, ''))
        return crumb_list

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
