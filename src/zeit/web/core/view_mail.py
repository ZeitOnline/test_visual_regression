import logging

import pyramid.httpexceptions
import pyramid.request
import zope.component

import zeit.content.article.interfaces
import zeit.content.author.interfaces
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
        success = captcha.verify(
            self.request.POST.get('g-recaptcha-response'),
            self.request.POST.get('nojs'))
        if success:
            self.send()
        return self.render_original_view(success)

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

    def render_original_view(self, success):
        subrequest = pyramid.request.Request.blank(
            self.request.path, headers=dict(self.request.headers))
        # So the `mail` module template knows to render a success message
        subrequest.headers['X-Mail-Success'] = str(success)
        # We cannot simply copy POST into subrequest.POST because webob is too
        # strict and would require method to be POST as well -- but we want GET
        for key, value in self.request.POST.items():
            subrequest.headers['X-POST-%s' % key] = value

        response = self.request.invoke_subrequest(subrequest, use_tweens=True)
        if response.status_int != 200:
            log.error('Error rendering %s after POST', self.request.url)
            raise pyramid.httpexceptions.HTTPInternalServerError()

        response.cache_expires(0)
        return response

@zeit.web.view_config(context=zeit.content.author.interfaces.IAuthor,
                      request_method='POST')
class AuthorMail(SendMail):

    @zeit.web.reify
    def recipient(self):
        if not self.context.email:
            message = 'No mail module found for POST to %s' % self.context
            log.error(message)
            raise RuntimeError(message)
        return self.context.email
