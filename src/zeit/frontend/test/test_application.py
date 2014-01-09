from zeit.frontend.application import Application
import zope.component
import zeit.cms.repository.interfaces

def test_empty_repository_path_should_resolve_topackage_path():
    app = Application()
    assert app.get_repository_path().endswith('zeit/frontend/data')

def test_repository_path_in_settings_should_be_used():
    app = Application()
    app.settings['repository_path'] = 'my/repo/path'
    assert app.get_repository_path().endswith('my/repo/path')

def test_default_application_should_have_test_repository(application):
    utility = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
    assert utility.connector.repository_path.endswith('zeit/frontend/data')
