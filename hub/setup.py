#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit('Python < 3.6 is not supported')

setup(
    name='overwatch-hub',
    version='2.0.0',
    description='Overwatch monitoring system data hub',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
    install_requires=[
        'aiohttp',
        'motor',
        'pyyaml',
        'simplejson',
    ],
    entry_points={
        'console_scripts': [
            'overwatch-hub=overwatch_hub:hub_main',
        ],
    })
