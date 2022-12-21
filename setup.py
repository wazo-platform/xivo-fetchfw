#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup, find_packages

setup(
    name='xivo-fetchfw',
    version='1.0',
    description='Library and tool for downloading and installing remote files.',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['xivo-fetchfw = xivo_fetchfw.main:main'],
    },
)
