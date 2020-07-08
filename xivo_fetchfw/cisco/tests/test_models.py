# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
