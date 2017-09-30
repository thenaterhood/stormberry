#!/usr/bin/env python

from setuptools import setup
import sys
import os

install_requires = [
    'sense-hat',
    ]

test_requires = [
    ]

data_files =[
        ]


setup(name='stormberry',
    version='0.1.0',
    description='Raspberry Pi weather station with plugins',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/stormberry/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    entry_points={
        'console_scripts': [
            'stormberry = stormberry.__main__:main'
        ]
    },
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'stormberry',
        'stormberry.storage_strategy'
        ],
    data_files=data_files,
    package_data={
        }
    )
