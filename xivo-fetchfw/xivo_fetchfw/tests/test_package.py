# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
import xivo_fetchfw.package as package


class TestInstalledPackage(unittest.TestCase):
    def test_ok_on_all_mandatory_keys_specified(self):
        pkg_info = {'id': 'foo',
                    'description': 'Foo',
                    'version': '1',
                    'files': [],
                    'explicit_install': True}
        package.InstalledPackage(pkg_info)

    def test_raise_error_on_missing_mandatory_key(self):
        pkg_info = {'id': 'foo',
                    'description': 'Foo',
                    'version': '1',
                    'files': [], }
        self.assertRaises(Exception, package.InstalledPackage, pkg_info)


class TestInstallablePackage(unittest.TestCase):
    def test_ok_on_all_mandatory_keys_specified(self):
        pkg_info = {'id': 'foo',
                    'description': 'Foo',
                    'version': '1'}
        package.InstallablePackage(pkg_info, [], None)

    def test_raise_error_on_missing_mandatory_key(self):
        pkg_info = {'id': 'foo',
                    'description': 'Foo'}
        self.assertRaises(Exception, package.InstallablePackage, pkg_info, [], None)
