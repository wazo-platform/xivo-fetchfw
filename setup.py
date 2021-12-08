#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import
from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-fetchfw',
    version='1.0',
    description='Library and tool for downloading and installing remote files.',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
)
