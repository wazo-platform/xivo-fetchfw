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

from mock import patch, Mock
from xivo_fetchfw.cisco.firmware_download import download_firmware
from xivo_fetchfw.cisco.errors import DownloadError, MetadataError

MODEL = "SPA9000"
LOCATION = "/tmp"
URL = "http://example.com"
GUID = "1234567890ABCDEFGHIJ1234567890ABCDEFGHIJ"
FLOWID = '5285'


class TestFirmwareDownloader(unittest.TestCase):

    @patch('xivo_fetchfw.cisco.models.generate_url')
    @patch('xivo_fetchfw.cisco.models.flowid_for_model')
    @patch('xivo_fetchfw.cisco.guid_extract.extract_from_url')
    @patch('xivo_fetchfw.cisco.metadata_download.download_metadata')
    @patch('xivo_fetchfw.cisco.file_download.download_from_metadata')
    def test_download_for_invalid_metadata(self, download_from_metadata, download_metadata, extract_from_url, flowid_for_model, generate_url):
        generate_url.return_value = URL
        extract_from_url.return_value = GUID
        download_from_metadata.side_effect = MetadataError('model')

        self.assertRaises(MetadataError, download_firmware, MODEL, LOCATION)
        generate_url.assert_called_once_with(MODEL)
        extract_from_url.assert_called_once_with(URL)

    @patch('xivo_fetchfw.cisco.models.generate_url')
    @patch('xivo_fetchfw.cisco.models.flowid_for_model')
    @patch('xivo_fetchfw.cisco.guid_extract.extract_from_url')
    @patch('xivo_fetchfw.cisco.metadata_download.download_metadata')
    @patch('xivo_fetchfw.cisco.file_download.download_from_metadata')
    def test_download_when_file_download_fails(self, download_from_metadata, download_metadata, extract_from_url, flowid_for_model, generate_url):
        generate_url.return_value = URL
        flowid_for_model.return_value = FLOWID

        extract_from_url.return_value = GUID
        download_from_metadata.side_effect = IOError()

        self.assertRaises(DownloadError, download_firmware, MODEL, LOCATION)
        generate_url.assert_called_once_with(MODEL)
        extract_from_url.assert_called_once_with(URL)
        flowid_for_model.assert_called_once_with(MODEL)

    @patch('xivo_fetchfw.cisco.models.generate_url')
    @patch('xivo_fetchfw.cisco.models.flowid_for_model')
    @patch('xivo_fetchfw.cisco.guid_extract.extract_from_url')
    @patch('xivo_fetchfw.cisco.metadata_download.download_metadata')
    @patch('xivo_fetchfw.cisco.file_download.download_from_metadata')
    def test_download(self, download_from_metadata, download_metadata, extract_from_url, flowid_for_model, generate_url):
        generate_url.return_value = URL
        extract_from_url.return_value = GUID
        flowid_for_model.return_value = FLOWID

        metadata = Mock()

        download_metadata.return_value = metadata

        download_firmware(MODEL, LOCATION)
        generate_url.assert_called_once_with(MODEL)
        extract_from_url.assert_called_once_with(URL)
        flowid_for_model.assert_called_once_with(MODEL)
        download_from_metadata.assert_called_once_with(metadata, LOCATION)
