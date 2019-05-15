#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages


setup(
    name='overwatch-ping-agent',
    version='2.0.0',
    description='Overwatch monitoring system MongoDB stats agent',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
    install_requires=[
        'pyyaml',
        'pymongo',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'overwatch-mongodb-stats-agent=overwatch_mongodb_stats_agent:mongodb_stats_agent_main',
        ],
    })
