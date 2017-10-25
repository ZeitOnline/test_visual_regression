import logging

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
class SendMail(zeit.web.core.view.Base):

    def __call__(self):
        super(SendMail, self).__call__()
        captcha = zope.component.getUtility(zeit.web.core.interfaces.ICaptcha)
        if not captcha.verify(self.request.POST.get('g-recaptcha-response')):
            return self.render_failure_view()
        else:
            self.send()
            return self.render_original_view()

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

    def render_original_view(self):
        subrequest = pyramid.request.Request.blank(
            self.request.path, headers=dict(self.request.headers))
        # So the `mail` module template knows to render a success message
        subrequest.headers['X-Mail-Success'] = 'True'

        response = self.request.invoke_subrequest(subrequest, use_tweens=True)
        if response.status_int != 200:
            log.error('Error rendering %s after POST', self.request.url)
            raise pyramid.httpexceptions.HTTPInternalServerError()

        response.cache_expires(0)
        return response

    def render_failure_view(self):
        subrequest = pyramid.request.Request.blank(
            self.request.path, headers=dict(self.request.headers))
        # So the `mail` module template knows to render a failure message
        subrequest.headers['X-Mail-Failure'] = 'True'

        post = self.request.POST
        body = post['body']
        subrequest.headers['Textarea'] = body

        response = self.request.invoke_subrequest(subrequest, use_tweens=True)
        return response
