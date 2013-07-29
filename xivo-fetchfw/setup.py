#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from distutils.core import setup

setup(
    name='xivo-fetchfw',
    version='1.0',
    description='Library and tool for downloading and installing remote files.',
    maintainer='Proformatique',
    maintainer_email='technique@proformatique.com',
    url='http://wiki.xivo.fr/',
    license='GPLv3',
    packages=['xivo_fetchfw',
              'xivo_fetchfw.cisco'],
    scripts=['bin/xivo-fetchfw'],
    data_files=[('/etc/pf-xivo', ['resources/etc/xivo-fetchfw.conf']),
                ('/var/lib/xivo-fetchfw/installable',
                      ['resources/data/files.db',
                       'resources/data/install.db',
                       'resources/data/packages.db'])]
)
