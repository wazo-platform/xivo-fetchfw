# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_fetchfw.cisco import models


class TestGenerateUrl(unittest.TestCase):

    def test_generate_url_no_model(self):
        models.MODELS.clear()
        model = 'SPA8000'

        self.assertRaises(models.NoInfoOnModelError, models.generate_url, model)

    def test_generate_url(self):
        model = 'SPA8000'
        models.MODELS[model] = [('mdfid', '282414110'), ('flowid', '5964'), ('softwareid', '282463187'), ('release', '6.1.11')]

        expected = "http://www.cisco.com/cisco/software/release.html?mdfid=282414110&softwareid=282463187&release=6.1.11"
        result = models.generate_url(model)

        self.assertEquals(result, expected)

    def test_flowid_for_model(self):
        model = 'SPA8000'
        models.MODELS[model] = [('mdfid', '282414110'), ('flowid', '5964'), ('softwareid', '282463187'), ('release', '6.1.11')]

        expected = '5964'
        result = models.flowid_for_model(model)

        self.assertEquals(result, expected)
