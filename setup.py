from setuptools import setup, find_packages

setup(
    name='zeit.frontend',
    version='0.1.dev0',

    install_requires=[
        'Babel',
        'grokcore.component',
        'iso8601',
        'lxml',
        'martian',
        'pyramid',
        'pyramid_jinja2',
        'setuptools',
        'simplejson',
        'supervisor',
        'waitress',
        'zeit.cms',
        'zeit.connector >= 2.1.0.dev0',
        'zeit.content.article',
        'zeit.intrafind',
        'zope.app.appsetup',
        'zope.configuration',
    ],
    entry_points={
        'paste.app_factory': [
            'main=zeit.frontend.application:factory',
        ],
    },
    extras_require={
        'test': [
            'mock',
        ],
    },
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
