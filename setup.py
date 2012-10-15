#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Smart-Grid-Controller',
    version='0.5',
    url='https://github.com/dmr/smart-grid-controller',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description='An implementation for a Smart Grid Controller',
    long_description=open('README.md').read(),

    packages=[
        'smart_grid_controller',
        'smart_grid_controller.test'
    ],

    entry_points={
        'console_scripts': [
            'smart_grid_controller = smart_grid_controller:main',
            ],
        },

    zip_safe=False,
    platforms='any',

    dependency_links = [
        'https://github.com/dmr/csp-solver/tarball/master#egg=csp_solver',
        'https://github.com/dmr/smart-grid-actor/tarball/master#egg=smart_grid_actor'
    ],

    install_requires=[
        'csp_solver',
        'smart_grid_actor',
        'argparse',
        'eventlet',

        #'spec', # for tests
        #'requests', # for tests
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        ]
)
