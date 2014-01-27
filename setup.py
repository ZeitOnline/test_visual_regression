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
        'zeit.cms',
        'zeit.connector >= 2.2',
        'zeit.content.article',
        'zeit.intrafind',
        'zeit.magazin',
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
            'pytest',
            'pytest-localserver',
            'pytest-pep8',
            'repoze.bitblt',
            'requests',
            'selenium',
            'webtest',
            'zope.testbrowser',
        ],
    },
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
