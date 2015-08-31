import re

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
                'http://{}/index'.format(self.request.host)
            ),
            'zmo': (
                'ZEIT Magazin',
                'http://{}/zeit-magazin/index'.format(self.request.host)
            ),
            'leben': (
                'Leben',
                'http://{}/zeit-magazin/leben/index'.format(self.request.host)
            ),
            'mode-design': (
                'Mode & Design',
                'http://{}/zeit-magazin/mode-design/index'.format(
                    self.request.host)
            ),
            'essen-trinken': (
                'Essen & Trinken',
                'http://{}/zeit-magazin/essen-trinken/index'.format(
                    self.request.host)
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
        cases = {
            'viewport_zoom': 'tablet-landscape',
        }
        return cases.get(name, None)

    @zeit.web.reify
    def adcontroller_handle(self):
        if self.is_hp:
            return 'zm_index'
        if self.type == 'centerpage':
            return 'zm_centerpage'
        return 'zm_artikel'

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore."""
        levels = self.banner_channel.replace('zeitmz/', '')
        levels = levels.split('/')
        # remove type from level3
        try:
            levels[1] = '' if levels[1] == self.type else levels[1]
        except IndexError:
            if levels[0] == 'centerpage':
                levels[0] = 'homepage'
            levels.append('')
        return [('$handle', self.adcontroller_handle),
                ('level2', "".join(re.findall(r"[A-Za-z0-9_]*", levels[0]))),
                ('level3', "".join(re.findall(r"[A-Za-z0-9_]*", levels[1]))),
                ('level4', ''),
                ('$autoSizeFrames', True),
                ('keywords', ','.join(self.adwords)),
                ('tma', '')]
