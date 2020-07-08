# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import urllib

from mock import Mock, sentinel
from xivo_fetchfw.cisco import file_download

GUID = 'testguid'
FLOWID = 'flowid'
DOWNLOAD_URL = 'http://example.com'
RANDOM_NUMBER = '4-H5Wvi8A0WrHnuCRM0WY0HOaN%2FgAcJ7NtYdENIQ84qvtGw%2FrE80wFpM3dRmIt8CDh'
IS_CLOUD = True
FILENAME = 'filename'


class TestFileDownload(unittest.TestCase):

    def test_download_from_metadata(self):
        metadata = {'download_url': DOWNLOAD_URL,
                    'is_cloud': IS_CLOUD,
                    'random_number': RANDOM_NUMBER,
                    'filename': FILENAME}

        expected_params = urllib.urlencode({'X-Authentication-Control': RANDOM_NUMBER})

        opener = Mock()
        opener.open.return_value = sentinel.reader

        reader = file_download.download_from_metadata(metadata, opener)

        opener.open.assert_called_with(DOWNLOAD_URL, expected_params)
        self.assertTrue(reader is sentinel.reader)

    def test_download_from_metadata_not_cloud(self):
        metadata = {'download_url': DOWNLOAD_URL,
                    'is_cloud': False,
                    'random_number': RANDOM_NUMBER,
                    'filename': FILENAME}

        opener = Mock()
        opener.open.return_value = sentinel.reader

        reader = file_download.download_from_metadata(metadata, opener)

        opener.open.assert_called_with(DOWNLOAD_URL)
        self.assertTrue(reader is sentinel.reader)
