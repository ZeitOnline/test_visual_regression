#!/usr/bin/python

from setuptools import setup, find_packages


setup(
    name='zeit.web',
    url='https://github.com/ZeitOnline/zeit.web',
    version='3.6',
    author=(
        'Thomas Baumann, Nico Bruenjes, Nicolas Drebenstedt, Ron Drongowski, '
        'Dominik Hoppe, Marco Kaiser, Harry Keller, Tom Lazar, Thomas Lotze, '
        'Malte Modrow, Thomas Puppe, Wolfgang Schnerring, Arne Seemann, '
        'Moritz Stoltenburg, Anika Szuppa, Christian Zagrodnick, '
        'Andreas Zeidler'
    ),
    author_email=(
        'thomas.baumann@zeit.de, nico.bruenjes@zeit.de, '
        'nicolas.drebenstedt@zeit.de, ron.drongowski@zeit.de, '
        'dominik.hoppe@zeit.de, marco.kaiser@zeit.de, ich@harry-k.de, '
        'tom@tomster.org, tl@gocept.com, malte.modrow@zeit.de, '
        'thomas.puppe@zeit.de, ws@gocept.com, arne.seemann@zeit.de, '
        'moritz.stoltenburg@zeit.de, anika.szuppa@zeit.de, cz@gocept.de, '
        'az@zitc.de'
    ),
    install_requires=[
        'Babel',
        'ProxyTypes',
        'PyJWT',
        'bugsnag',
        'colander',
        'cryptography',
        'dogpile.cache',
        'python-dateutil',
        'grokcore.component',
        'iso8601',
        'lxml',
        'martian',
        'pyramid',
        'pyramid_debugtoolbar',
        'pyramid_dogpile_cache2',
        'pyramid_jinja2',
        'pyramid_mako',
        'pyramid_tm',
        'pyramid_zodbconn',
        'python-statsd',
        'pytz',
        'requests',
        'requests-file',
        'setuptools',
        'wsgiproxy',
        'zc.iso8601',
        'zc.sourcefactory',
        'zeit.brightcove',
        'zeit.cms>=2.87.0.dev0',
        'zeit.campus>=1.6.0.dev0',
        'zeit.connector>=2.8.0.dev0',
        'zeit.content.advertisement',
        'zeit.content.article>=3.18.0.dev0',
        'zeit.content.author>=2.6.0.dev0',
        'zeit.content.cp>=3.10.0.dev0',
        'zeit.content.dynamicfolder',
        'zeit.content.gallery',
        'zeit.content.image>=2.16.0',
        'zeit.content.infobox',
        'zeit.content.link',
        'zeit.content.portraitbox',
        'zeit.content.quiz',
        'zeit.content.text',
        'zeit.content.video',
        'zeit.edit',
        'zeit.find',
        'zeit.intrafind',
        'zeit.magazin',
        'zeit.newsletter',
        'zeit.push>=1.13.0.dev0',
        'zeit.retresco>=1.3.1.dev0',
        'zeit.seo>=1.7.0.dev0',
        'zeit.solr',
        'zeit.vgwort',
        'zeit.website',
        'zeit.wysiwyg',
        'zope.app.appsetup',
        'zope.component',
        'zope.configuration',
        'zope.processlifetime'
    ],
    description='This package is all about ZEIT ONLINE website delivery.',
    long_description=open('README.md', 'r').read(),
    entry_points={
        'paste.app_factory': [
            'main=zeit.web.core.application:factory'
        ]
    },
    extras_require={
        'test': [
            'cssselect',
            'gocept.httpserverlayer',
            'mock',
            'plone.testing [zca,zodb]',
            'pytest',
            'pytest-pep8',
            'pytest-timeout',
            'selenium',
            'transaction',
            'waitress',
            'webtest',
            'wesgi',
            'zope.event',
            'zope.testbrowser [wsgi]'
        ]
    },
    setup_requires=['setuptools_git'],
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    keywords='web wsgi pyramid zope',
    license='Proprietary license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pyramid',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI'
    ]
)
