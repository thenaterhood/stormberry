#!/usr/bin/env python

from setuptools import setup
import sys
import os
import glob

install_requires = [
    'sense-hat',
    'yapsy',
    'flask',
    'flask_cors'
    ]

test_requires = [
    ]

yapsy_files = glob.glob('src/stormberry/pluggable/*.*')
server_files = glob.glob('src/stormberry/server/static/*.*')
js_files = glob.glob('src/stormberry/server/static/assets/js/*.*')
css_files = glob.glob('src/stormberry/server/static/assets/css/*.*')

data_files =[
        ('/etc/stormberry', ['config.ini.example']),
        ('/lib/stormberry/plugins_available', ['README.md']),
        ('/lib/stormberry/plugins_enabled', ['README.md']),
        ('/lib/stormberry/plugins_available', yapsy_files),
        ('/lib/stormberry/static_files', server_files),
        ('/lib/stormberry/static_files/assets/js', js_files),
        ('/lib/stormberry/static_files/assets/css', css_files)
        ]


setup(name='stormberry',
    version='1.1.0',
    description='Raspberry Pi weather station with plugins',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/stormberry/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    entry_points={
        'console_scripts': [
            'stormberry = stormberry.station.__main__:main',
            'stormberry-demo-server = stormberry.server.server:demo'
        ]
    },
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'stormberry',
        'stormberry.forecast',
        'stormberry.interpreter',
        'stormberry.logging',
        'stormberry.server',
        'stormberry.server.api',
        'stormberry.server.api.grafana',
        'stormberry.server.api.forecast',
        'stormberry.server.api.comfort',
        'stormberry.server.api.weather',
        'stormberry.server.api.pollution',
        'stormberry.station',
        'stormberry.plugin',
        'stormberry.pluggable',
        'stormberry.util'
        ],
    data_files=data_files,
    package_data={
        }
    )
