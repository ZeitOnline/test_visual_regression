#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='zeit.frontend',
    version='0.9',
    author=(
        'Thomas Baumann, Nico Brünjes, Nicolas Drebenstedt, Ron Drongowski, '
        'Dominik Hoppe, Marco Kaiser, Harry Keller, Tom Lazar, Thomas Lotze, '
        'Malte Modrow, Wolfgang Schnerring, Arne Seemann, Moritz Stoltenburg, '
        'Anika Szuppa, Christian Zagrodnick, Andreas Zeidler'
    ),
    author_email=(
        'thomas.baumann@zeit.de, nico.bruenjes@zeit.de, '
        'nicolas.drebenstedt@zeit.de, ron.drongowski@zeit.de, '
        'dominik.hoppe@zeit.de, marco.kaiser@zeit.de, ich@harry-k.de, '
        'tom@tomster.org, tl@gocept.com, malte.modrow@zeit.de, ws@gocept.com, '
        'arne.seemann@zeit.de, moritz.stoltenburg@zeit.de, '
        'anika.szuppa@zeit.de, cz@gocept.de, az@zitc.de'
    ),
    install_requires=[
        'Babel',
        'cornice >= 0.16.2',
        'colander',
        'grokcore.component',
        'iso8601',
        'lxml',
        'martian',
        'pyramid',
        'pyramid_beaker',
        'pyramid_jinja2',
        'pyramid_tm',
        'pyramid_debugtoolbar',
        'pyramid_mako',
        'pytz',
        'repoze.bitblt',
        'repoze.vhm',
        'requests',
        'setuptools',
        'zc.iso8601',
        'wsgiproxy',
        'zeit.cms',
        'zeit.connector >= 2.3.3.dev0',
        'zeit.content.article',
        'zeit.content.author',
        'zeit.content.cp',
        'zeit.content.gallery',
        'zeit.content.image',
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
        'zeit.newsletter >= 1.0.0b2.dev0',
        'zeit.wysiwyg',
        'zeit.seo',
        'zope.app.appsetup',
        'zope.component',
        'zope.configuration',
        'zope.processlifetime',
    ],
    entry_points={
        'paste.app_factory': [
            'main=zeit.frontend.application:factory',
            'preview=zeit.frontend.preview:factory',
        ],
    },
    extras_require={
        'test': [
            'gocept.httpserverlayer',
            'cssselect',
            'mock',
            'webtest',
            'pytest',
            'pytest-pep8',
            'selenium',
            'waitress',
            'webtest',
            'zope.testbrowser [wsgi]',
        ],
    },
    setup_requires=['setuptools_git'],
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
