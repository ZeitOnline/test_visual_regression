import zeit.magazin.interfaces

import zeit.web.core.view


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'


class Base(zeit.web.core.view.Base):

    seo_title_default = (
        u'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben')
    pagetitle_suffix = u' | ZEITmagazin'

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

    def banner_toggles(self, name):
        # no banner toggles in ZMO in the moment
        return True

    @zeit.web.reify
    def deliver_ads_oldschoolish(self):
        # old school ads in ZMO
        return True
