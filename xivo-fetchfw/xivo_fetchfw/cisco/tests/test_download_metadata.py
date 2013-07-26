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
import os
import json

from mock import Mock
from xivo_fetchfw.cisco.metadata_download import MetadataError, download_metadata

FLOWID = 'flowid'
GUID = 'testguid'


class TestMetadataDownload(unittest.TestCase):

    SAMPLE_JSON = 'downloadjson.json'
    SAMPLE_DOWNLOAD_URL = 'https://secure-global.esd.cisco.com/files/swc/sec/4_SDSP_688502_1341980285918/1/SPA8000_6.1.11_FW.zip?ip=72.163.9.198&dtrTag=4_SDSP_688502_1341980285918_04656ca0574d28b9b390ad923af77d27&userid=null&tenant-id=sdsp&__gda__=1373719358_add3180ac1dcca61707c2054aefb323941f7f1da46f62b7fe08be5f1443030fa'
    SAMPLE_RANDOM_NUMBER = '4-H5Wvi8A0WrHnuCRM0WY0HOaN%2FgAcJ7NtYdENIQ84qvtGw%2FrE80wFpM3dRmIt8CDh'
    SAMPLE_ISCLOUD = True
    SAMPLE_FILENAME = 'SPA8000_6.1.11_FW.zip'

    def test_extract_download_metadata(self):
        reader = Mock()
        reader.read.return_value = self._json_from_sample()
        opener = Mock()
        opener.open.return_value = reader

        expected_json_url = 'http://www.cisco.com/cisco/software/cart/service?a=downloadnow&imageGuId=%s&sa=&rnp=&k9=&eula=&atc=N&flowid=%s&config=&hAcl=' % (GUID, FLOWID)

        expected = {'download_url': self.SAMPLE_DOWNLOAD_URL,
                    'random_number': self.SAMPLE_RANDOM_NUMBER,
                    'is_cloud': self.SAMPLE_ISCLOUD,
                    'filename': self.SAMPLE_FILENAME}

        result = download_metadata(GUID, FLOWID, opener)

        opener.open.assert_called_once_with(expected_json_url)
        self.assertEquals(result, expected)

    def _json_from_sample(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, self.SAMPLE_JSON)
        samplejson = open(path).read()
        return samplejson

    def test_extract_download_metadata_no_json(self):
        reader = Mock()
        reader.read.return_value = ''
        opener = Mock()
        opener.open.return_value = reader

        self.assertRaises(MetadataError, download_metadata, GUID, FLOWID, opener)

    def test_extract_download_metadata_no_properties(self):
        reader = Mock()
        reader.read.return_value = '{}'
        opener = Mock()
        opener.open.return_value = reader

        self.assertRaises(MetadataError, download_metadata, GUID, FLOWID, opener)

    def test_extract_download_metadata_no_url_list(self):
        reader = Mock()
        reader.read.return_value = json.dumps({'dwldValidationSerResponse': {}})
        opener = Mock()
        opener.open.return_value = reader

        self.assertRaises(MetadataError, download_metadata, GUID, FLOWID, opener)
