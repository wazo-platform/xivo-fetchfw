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

from xivo_fetchfw.cisco.models import ModelInfo


class TestModelInfo(unittest.TestCase):

    def test_generate_url(self):
        flow_id = '5964'
        url_params = [('mdfid', '282414110'), ('softwareid', '282463187'), ('release', '6.1.11')]
        model_info = ModelInfo(flow_id, url_params)

        expected = "http://www.cisco.com/cisco/software/release.html?mdfid=282414110&softwareid=282463187&release=6.1.11"
        result = model_info.generate_url()

        self.assertEquals(result, expected)
