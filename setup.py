#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from pip.req import parse_requirements
import os
import re
import shutil
import sys

with open("README.rst", "rb") as readme_file:
    readme = readme_file.read().decode("utf-8")    

with open('HISTORY.rst') as history_file:
    history = history_file.read()

embedded_libs = [
'ansible_taskrunner/lib/py2', 
'ansible_taskrunner/lib/py3'
]

for embedded_lib in embedded_libs:
    if os.path.isdir(embedded_lib):
        print('Removing embedded lib %s' % embedded_lib)
        shutil.rmtree(embedded_lib)

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)
# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
requirements = [str(ir.req) for ir in install_reqs]

# Derive version info from main module
try:
    version = re.search(
        '^__version__[\s]+=[\s]+(.*).*',
        open('ansible_taskrunner/__init__.py').read(),
        re.M
        ).group(1)
except AttributeError as e:
    print('''
        I had trouble determining the verison information from your app.
        Make sure the version string matches this format:
        __version__ = '1.0'
        ''')

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Engelbert Tejeda",
    author_email='berttejeda@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="ansible-playbook wrapper with YAML-abstracted python click cli options",
    entry_points={
        'console_scripts': [
            'tasks=ansible_taskrunner.cli:entrypoint',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ansible playbook wrapper bash python click task-runner subprocess yaml cli options',
    name='ansible_taskrunner',
    packages=find_packages(exclude=['py2','py3']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/berttejeda/ansible_taskrunner',
    version=version,
    zip_safe=False,
)
