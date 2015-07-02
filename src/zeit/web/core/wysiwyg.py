import pyramid.threadlocal
import pyramid.view
import pytz
import zc.iso8601.parse

import zeit.content.image.interfaces
import zeit.wysiwyg.html

import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_image


# Monkey-patches to zeit.wysiwyg to remove Zope-isms.
# These only concern the direction XML->HTML, since that's the one we need.


def init_without_request(self, context, converter):
    self.context = context
    self.converter = converter
zeit.wysiwyg.html.ConversionStep.__init__ = init_without_request


def pyramid_url(self, obj):
    request = pyramid.threadlocal.get_current_request()
    return zeit.web.core.template.create_url(None, obj.uniqueId, request)
zeit.wysiwyg.html.ConversionStep.url = pyramid_url


def datetime_to_html(self, dt_string):
    dt = ''
    if dt_string:
        try:
            dt = zc.iso8601.parse.datetimetz(dt_string)
        except ValueError:
            pass
        else:
            dt = dt.astimezone(pytz.timezone('Europe/Berlin')).strftime(
                '%Y-%m-%d %H:%M')
    return dt
zeit.wysiwyg.html.ConversionStep.datetime_to_html = datetime_to_html


@pyramid.view.view_config(context=zeit.content.image.interfaces.IImage,
                          name='@@raw')
class ImageView(zeit.web.core.view_image.Image):
    """Since zeit.wysiwyg.html.ImageStep.to_html insists on creating
    an URL that ends in '/@@raw', we need to oblige.

    NOTE: That we configure a view in this file also ensures it being imported
    so the monkey patches are triggered.
    """
