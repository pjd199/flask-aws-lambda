#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2021 Nik Ho
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import codecs
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    try:
        f = codecs.open(os.path.join(here, *file_paths), 'r', 'latin1')
        version_file = f.read()
        f.close()
    except:
        raise RuntimeError("Unable to find version string.")

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the relevant file
try:
    f = codecs.open('README.rst', encoding='utf-8')
    long_description = f.read()
    f.close()
except:
    long_description = ''

try:
    f = codecs.open('requirements.txt', encoding='utf-8')
    requirements = f.read().splitlines()
    f.close()
except:
    requirements = []


setup(
    name='flask-aws-lambda',
    version=find_version('flask_aws_lambda.py'),
    description=('Python module to make Flask compatible with AWS Lambda for '
                 'creating RESTful applications. Compatible with both REST '
                 'and HTTP API gateways.'),
    long_description=long_description,
    keywords='flask aws amazon lambda',
    author='Nik Ho',
    author_email='codeschwert@protonmail.com',
    url='https://github.com/CodeSchwert/flask-aws-lambda',
    download_url='https://github.com/CodeSchwert/flask-aws-lambda/archive/refs/tags/v1.0.1.tar.gz',
    license='Apache License, Version 2.0',
    py_modules=['flask_aws_lambda'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ]
)
