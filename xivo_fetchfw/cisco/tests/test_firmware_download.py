# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import patch, Mock
from xivo_fetchfw.cisco.firmware_download import download_firmware
from xivo_fetchfw.cisco.errors import MetadataError
from xivo_fetchfw.cisco.models import ModelInfo

URL = "http://example.com"
GUID = "1234567890ABCDEFGHIJ1234567890ABCDEFGHIJ"
FLOWID = '5285'


class TestFirmwareDownloader(unittest.TestCase):

    @patch('xivo_fetchfw.cisco.guid_extract.extract_from_url')
    @patch('xivo_fetchfw.cisco.metadata_download.download_metadata')
    @patch('xivo_fetchfw.cisco.file_download.download_from_metadata')
    def test_download_for_invalid_metadata(self, download_from_metadata, download_metadata, extract_from_url):
        model_info = Mock(ModelInfo)
        model_info.flow_id = FLOWID
        model_info.generate_url.return_value = URL
        extract_from_url.return_value = GUID
        download_from_metadata.side_effect = MetadataError('model')

        opener = Mock()

        self.assertRaises(MetadataError, download_firmware, model_info, opener)

        model_info.generate_url.assert_called_once_with()
        extract_from_url.assert_called_once_with(URL, opener)

    @patch('xivo_fetchfw.cisco.guid_extract.extract_from_url')
    @patch('xivo_fetchfw.cisco.metadata_download.download_metadata')
    @patch('xivo_fetchfw.cisco.file_download.download_from_metadata')
    def test_download(self, download_from_metadata, download_metadata, extract_from_url):
        model_info = Mock(ModelInfo)
        model_info.flow_id = FLOWID
        model_info.generate_url.return_value = URL
        extract_from_url.return_value = GUID

        metadata = Mock()
        opener = Mock()

        download_metadata.return_value = metadata

        download_firmware(model_info, opener)

        model_info.generate_url.assert_called_once_with()
        extract_from_url.assert_called_once_with(URL, opener)
        download_from_metadata.assert_called_once_with(metadata, opener)
