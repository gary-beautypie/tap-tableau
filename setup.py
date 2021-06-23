#!/usr/bin/env python

from setuptools import setup

setup(name='tap-tableau',
      version='0.0.1',
      description='Singer tap for extracting data from the Tableau API',
      author='Beauty Pie',
      url='https://beautypie.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_github'],
      install_requires=[
          'singer-python==5.12.1',
          'requests==2.20.0',
          'tableauserverclient==0.15.0'
      ],
      extras_require={
          'dev': [
              'pylint',
              'ipdb',
              'nose',
          ]
      },
      entry_points='''
          [console_scripts]
          tap-tableau=tap_tableau:main
      ''',
      packages=['tap_tableau'],
      package_data = {
          'tap_tableau': ['tap_tableau/schemas/*.json']
      },
      include_package_data=True
)
