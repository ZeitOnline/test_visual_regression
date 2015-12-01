import pyramid.view

import zeit.content.author.interfaces

from zeit.web.site.view_centerpage import LegacyArea, LegacyRegion
import zeit.web.site.view


@zeit.web.register_module('author_header')
class AuthorHeader(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorHeader, self).__init__(context)
        self.layout = 'author_header'

    @zeit.web.reify
    def name(self):
        return self.context.display_name

    @zeit.web.reify
    def position(self):
        # XXX Get info from xml
        return 'Redakteur(in) im Ressort Politik, ZEIT ONLINE'

    @zeit.web.reify
    def image_group(self):
        return self.context.image_group


@pyramid.view.view_config(
    renderer='templates/author.html',
    context=zeit.content.author.interfaces.IAuthor)
class Author(zeit.web.core.view.Base):

    advertising_enabled = True

    @zeit.web.reify
    def pagetitle(self):
        return self.context.display_name

    @zeit.web.reify
    def pagedescription(self):
        return self.context.display_name

    @zeit.web.reify
    def ranked_tags_list(self):
        return ''

    @zeit.web.reify
    def js_vars(self):
        return ''

    @zeit.web.reify
    def banner_channel(self):
        return ''

    @zeit.web.reify
    def ressort(self):
        return ''

    @zeit.web.reify
    def sub_ressort(self):
        return ''

    @zeit.web.reify
    def serie(self):
        return ''

    @zeit.web.reify
    def regions(self):
        regions = []

        module = AuthorHeader(self.context)
        regions.append(LegacyRegion([LegacyArea([module])]))

        return regions

        # region(
        #     area(
        #         author_header))

        # region(
        #     area(
        #         schwerpunkte,
        #         minibio,
        #         fragen),
        #     area(
        #          kontaktdaten)

        # region([
        #        area(
        #             AuthorenTexte),
        #        area(
        #             AutorenKommentare])
