#!/usr/bin/python

from setuptools import setup, find_packages


setup(
    name='zeit.web',
    url='https://github.com/ZeitOnline/zeit.web',
    version='3.149',
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
        'Jinja2 >= 2.10.0.dev0',
        'colander',
        'cryptography',
        'dogpile.cache',
        'python-dateutil',
        'gocept.cache',
        'grokcore.component',
        'iso8601',
        'lxml',
        'martian',
        'pyramid >= 1.6.0',
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
        'zeit.arbeit>=1.2.2.dev0',
        'zeit.brightcove>=2.12.0.dev0',
        'zeit.cms>=3.2.0.dev0',
        'zeit.campus>=1.6.0.dev0',
        'zeit.connector>=2.9.0.dev0',
        'zeit.content.advertisement',
        'zeit.content.article>=3.38.0.dev0',
        'zeit.content.author>=2.6.0.dev0',
        'zeit.content.cp>=3.23.0.dev0',
        'zeit.content.dynamicfolder',
        'zeit.content.gallery>=2.7.4.dev0',
        'zeit.content.image>=2.20.0',
        'zeit.content.infobox>=1.25.0.dev0',
        'zeit.content.link',
        'zeit.content.portraitbox',
        'zeit.content.quiz',
        'zeit.content.text',
        'zeit.content.rawxml>=0.5.0.dev0',
        'zeit.content.video >= 3.0.0.dev0',
        'zeit.content.volume >= 1.6.0.dev0',
        'zeit.edit >= 2.16.0.dev0',
        'zeit.find',
        'zeit.magazin',
        'zeit.newsletter',
        'zeit.push>=1.13.0.dev0',
        'zeit.retresco>=1.21.0.dev0',
        'zeit.seo>=1.8.0.dev0',
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
            'pytest>=3.4.0.dev0',
            'pytest-pep8',
            'pytest-timeout',
            'requests-mock',
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
