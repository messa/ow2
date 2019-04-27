#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages


setup(
    name='overwatch-http-check-agent',
    version='2.0.0',
    description='Overwatch monitoring system data hub',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
    install_requires=[
        'aiohttp',
        'aiodns',
        'cchardet',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'overwatch-http-check-agent=overwatch_http_check_agent:http_check_agent_main',
        ],
    })
