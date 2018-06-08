import logging
import requests

import pyramid.httpexceptions
import pyramid.request
import zope.component

import zeit.content.article.interfaces
import zeit.content.modules.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.magazin.article

log = logging.getLogger(__name__)


class FormPostMixin(object):
    """
    Mixin for views which work with form data.
    """

    def render_original_view(self, success, success_header_name):
        subrequest = pyramid.request.Request.blank(
            self.request.path, headers=dict(self.request.headers))
        subrequest.headers['X-%s-Success' % success_header_name] = str(success)
        for key, value in self.request.POST.items():
            subrequest.headers['X-POST-%s' % key] = value

        response = self.request.invoke_subrequest(subrequest, use_tweens=True)
        if response.status_int != 200:
            log.error('Error rendering %s after POST', self.request.url)
            raise pyramid.httpexceptions.HTTPInternalServerError()

        response.cache_expires(0)
        return response


@zeit.web.view_defaults(
    request_param='action=mail')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      name='komplettansicht',
                      request_method='POST')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      name='seite',
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IShortformArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IColumnArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IPhotoclusterArticle,
                      request_method='POST')
class SendMail(FormPostMixin, zeit.web.core.view.Base):

    def __call__(self):
        super(SendMail, self).__call__()
        captcha = zope.component.getUtility(zeit.web.core.interfaces.ICaptcha)
        success = captcha.verify(
            self.request.POST.get('g-recaptcha-response'),
            self.request.POST.get('nojs'))
        if success:
            self.send()
        return self.render_original_view(success, 'Mail')

    def send(self):
        mail = zope.component.getUtility(zeit.web.core.interfaces.IMail)
        post = self.request.POST
        body = post['body'] + u'\n\n-- \nGesendet von %s' % self.request.url
        log.info(
            'Sending email to %s at %s', self.recipient, self.request.path)
        mail.send(post['from'], self.recipient, post['subject'], body)

    @zeit.web.reify
    def recipient(self):
        module = self.context.body.find_first(
            zeit.content.modules.interfaces.IMail)
        if not module:
            message = 'No mail module found for POST to %s' % self.context
            log.error(message)
            raise RuntimeError(message)
        return module.to


@zeit.web.view_defaults(
    request_param='action=puzzle')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      name='komplettansicht',
                      request_method='POST')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      name='seite',
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IShortformArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IColumnArticle,
                      request_method='POST')
@zeit.web.view_config(context=zeit.web.magazin.article.IPhotoclusterArticle,
                      request_method='POST')
class SendPuzzleSolution(FormPostMixin, zeit.web.core.view.Base):

    def __call__(self):
        super(SendPuzzleSolution, self).__call__()
        success = self.send()
        return self.render_original_view(success, 'Puzzle')

    def send(self):
        """
        Send data to puzzle backend
        """
        json_data = self._build_data()
        log.info('Sending puzzle solution to %s at %s',
                 json_data, self.request.path)
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        backend_url = conf.get('puzzle_backend')
        # Otherwise a SELECT is triggered by postgREST to return the created
        # row and this route does not have this privilege
        response = requests.post(backend_url, json=json_data,
                                 headers={"Prefer": "return=minimal"})
        return response.status_code < 300

    def _build_data(self):
        result = dict()
        form_data = self.request.POST
        for required_field in [
                'type', 'year', 'first_name', 'name', 'street', 'city',
                'zipcode', 'e_mail', 'solution', 'country']:
            result[required_field] = form_data[required_field]
        result['agreement'] = bool(form_data.get('agreement')) or False
        for optional_field in ['phone', 'episode', 'points', 'coordinates']:
            result[optional_field] = form_data.get(optional_field)
        return result
