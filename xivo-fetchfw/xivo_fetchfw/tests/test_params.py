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
from xivo_fetchfw import params


class TestFilterSection(unittest.TestCase):
    def test_strip_section_name(self):
        config_dict = {'foo.a': 1}
        section_id = 'foo'
        expected = {'a': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_filter_correctly(self):
        config_dict = {'foo.a': 1, 'bar.b': 2}
        section_id = 'foo'
        expected = {'a': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_returns_empty_dict_on_no_match(self):
        config_dict = {'bar.b': 2}
        section_id = 'foo'
        expected = {}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_accept_empty_config_dict(self):
        config_dict = {}
        section_id = 'foo'
        expected = {}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_section_id_cant_contain_dot(self):
        self.assertRaises(ValueError, params.filter_section, {}, 'foo.bar')

    def test_option_id_can_contain_dot(self):
        config_dict = {'foo.a.b': 1}
        section_id = 'foo'
        expected = {'a.b': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)


class TestBool(unittest.TestCase):
    def test_true_raw_values(self):
        self.assertTrue(params.bool_('True'))
        self.assertTrue(params.bool_('true'))

    def test_false_raw_values(self):
        self.assertFalse(params.bool_('False'))
        self.assertFalse(params.bool_('false'))

    def test_invalid_raw_values(self):
        self.assertRaises(ValueError, params.bool_, '')
        self.assertRaises(ValueError, params.bool_, 'test')
