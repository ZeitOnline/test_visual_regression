#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='zeit.frontend',
    version='0.2.16.dev0',
    author=u'Thomas Baumann, Nico Brünjes, Ron Drongowski, Anika Szuppa',
    author_email='thomas.baumann@zeit.de, nico.bruenjes@zeit.de, \
                  ron.drongowski@zeit.de, anika.szuppa@zeit.de',
    install_requires=[
        'Babel',
        'cornice >= 0.16.2',
        'grokcore.component',
        'iso8601',
        'lxml',
        'martian',
        'pyramid',
        'pyramid_jinja2',
        'pyramid_tm',
        'setuptools',
        'simplejson',
        'zeit.cms',
        'zeit.connector >= 2.3',
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
            'webtest',
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
    setup_requires=['setuptools_git'],
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
