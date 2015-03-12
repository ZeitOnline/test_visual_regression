import zeit.web.core.interfaces
import zeit.web.site.view


def test_unpublished_breaking_news_should_be_detected(application):
    assert zeit.web.site.view.check_breaking_news() is False


def test_published_breaking_news_should_be_detected(application, monkeypatch):
    monkeypatch.setattr(
        zeit.workflow.workflow.ContentWorkflow, 'published', True)
    assert zeit.web.site.view.check_breaking_news() is True


def test_missing_breaking_news_should_eval_to_false(
        application, app_settings, ephemeral_settings):
    app_settings['breaking_news'] = 'moep'
    ephemeral_settings(app_settings)
    zeit.web.site.view.check_breaking_news()
