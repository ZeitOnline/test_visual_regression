# -*- coding: utf-8 -*-
import re

import pyramid.view

import zeit.magazin.interfaces

import zeit.web.core.security
import zeit.web.core.view


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    seo_title_default = (
        u'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben')
    pagetitle_suffix = u' | ZEITmagazin'

    def breadcrumbs_by_navigation(self, breadcrumbs=None):
        if breadcrumbs is None:
            breadcrumbs = []
        breadcrumbs = super(Base, self).breadcrumbs_by_navigation(breadcrumbs)
        navigation = {
            'zeit-magazin': (
                'ZEITmagazin',
                '{}zeit-magazin/index'.format(self.request.route_url('home'))
            ),
            'leben': (
                'Leben',
                '{}zeit-magazin/leben/index'.format(
                    self.request.route_url('home'))
            ),
            'mode-design': (
                'Mode & Design',
                '{}zeit-magazin/mode-design/index'.format(
                    self.request.route_url('home'))
            ),
            'essen-trinken': (
                'Essen & Trinken',
                '{}zeit-magazin/essen-trinken/index'.format(
                    self.request.route_url('home'))
            )
        }
        for segment in (self.ressort, self.sub_ressort):
            if segment == u'lebensart':
                segment = u'zeit-magazin'
            if segment in navigation:
                breadcrumbs.append(navigation[segment])
        return breadcrumbs

    @zeit.web.reify
    def ressort_literally(self):
        if self.is_hp or self.ressort == 'lebensart':
            return 'ZEITmagazin'
        ressorts = {
            'leben': 'Leben',
            'mode-design': 'Mode & Design',
            'essen-trinken': 'Essen & Trinken',
        }
        return ressorts.get(self.sub_ressort, self.ressort.capitalize())

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
        if self.type == 'gallery':
            return 'zm_galerie'
        return 'zm_artikel'

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore."""
        levels = self.banner_channel.split('/')
        # remove type from level3
        levels[1] = '' if levels[1] == self.type else levels[1]
        try:
            if self.is_hp:
                levels[1] = 'homepage'
        except IndexError:
            pass
        return [('$handle', self.adcontroller_handle),
                ('level2', "".join(re.findall(r"[A-Za-z0-9_]*", levels[0]))),
                ('level3', "".join(re.findall(r"[A-Za-z0-9_]*", levels[1]))),
                ('level4', ''),
                ('$autoSizeFrames', True),
                ('keywords', ','.join(self.adwords)),
                ('tma', '')]


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=magazin',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)
