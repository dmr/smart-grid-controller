#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Smart-Grid-Controller',
    version='1.0.0',
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
            'smart_grid_controller = smart_grid_controller.cli:main',
        ],
    },

    zip_safe=False,
    platforms='any',

    dependency_links = [
        'https://github.com/dmr/csp-solver/tarball/master#egg=csp_solver-0.4',
        'https://github.com/dmr/smart-grid-actor/tarball/master#egg=smart_grid_actor-1.0.0'
    ],

    install_requires=[
        'csp_solver>=0.4',
        'smart_grid_actor>=0.5.1',

        'argparse',
        'eventlet',

        #'unittest2',
        #'spec', # for tests
        #'requests', # for tests
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
