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
