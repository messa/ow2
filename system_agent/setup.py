#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages


setup(
    name='overwatch-system-agent',
    version='2.0.0',
    description='Overwatch monitoring system data hub',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
    install_requires=[
        'psutil',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'overwatch-system-agent=overwatch_system_agent:system_agent_main',
        ],
    })
