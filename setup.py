from setuptools import setup, find_packages

setup(
    name='zeit.frontend',
    version='0.1.dev0',

    install_requires=[
        'lxml',
        'pyramid',
        'pyramid_jinja2',
        'setuptools',
        'simplejson',
        'waitress',
    ],
    entry_points={
        'paste.app_factory': [
            'main=zeit.frontend.application:factory',
        ],
    },
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    zip_ok=False
)
