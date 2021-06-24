#!/usr/bin/env python
import pathlib
from setuptools import setup

setup(
    name='tap-tableau',
    version='0.0.5',
    description='Singer tap for extracting data from the Tableau API',
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author='gary.james@beautypie.com',
    url='https://github.com/gary-beautypie/tap-tableau',
    classifiers=['Programming Language :: Python :: 3 :: Only'],
    install_requires=[
        'singer-python==5.12.1',
        'requests==2.25.0',
        'tableauserverclient==0.15.0'
    ],
    extras_require={
        'dev': [
            'pylint',
            'nose',
        ]
    },
    entry_points='''
        [console_scripts]
        tap-tableau=tap_tableau:main
    ''',
    packages=['tap_tableau'],
    package_data={
        'tap_tableau': ['tap_tableau/schemas/*.json']
    },
    include_package_data=True
)
