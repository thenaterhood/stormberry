#!/usr/bin/env python

from setuptools import setup
import sys
import os
import glob

install_requires = [
    'sense-hat',
    'yapsy'
    ]

test_requires = [
    ]

yapsy_files = glob.glob('src/stormberry/pluggable/*.*')

data_files =[
        ('/etc/stormberry', ['config.ini']),
        ('/lib/stormberry/plugins_available', ['README.md']),
        ('/lib/stormberry/plugins_enabled', ['README.md']),
        ('/lib/stormberry/plugins_available', yapsy_files)
        ]


setup(name='stormberry',
    version='1.0.0',
    description='Raspberry Pi weather station with plugins',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/stormberry/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    entry_points={
        'console_scripts': [
            'stormberry = stormberry.station.__main__:main'
        ]
    },
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'stormberry',
        'stormberry.station',
        'stormberry.plugin',
        'stormberry.pluggable',
        'stormberry.util'
        ],
    data_files=data_files,
    package_data={
        }
    )
