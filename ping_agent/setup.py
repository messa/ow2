#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages


setup(
    name='overwatch-ping-agent',
    version='2.0.0',
    description='Overwatch monitoring system ping agent',
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
            'overwatch-ping-agent=overwatch_ping_agent:ping_agent_main',
        ],
    })
