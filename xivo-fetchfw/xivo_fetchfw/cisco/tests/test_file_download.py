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
import urllib

from mock import patch, Mock, mock_open
from xivo_fetchfw.cisco import file_download
from xivo_fetchfw.cisco.errors import DownloadError

GUID = 'testguid'
FLOWID = 'flowid'
DOWNLOAD_URL = 'http://example.com'
RANDOM_NUMBER = '4-H5Wvi8A0WrHnuCRM0WY0HOaN%2FgAcJ7NtYdENIQ84qvtGw%2FrE80wFpM3dRmIt8CDh'
IS_CLOUD = True
FILENAME = 'filename'


class TestFileDownload(unittest.TestCase):

    @patch('urllib2.urlopen')
    def test_download_from_metadata(self, urlopen):
        metadata = {'download_url': DOWNLOAD_URL,
                    'is_cloud': IS_CLOUD,
                    'random_number': RANDOM_NUMBER,
                    'filename': FILENAME}

        expected_params = urllib.urlencode({'X-Authentication-Control': RANDOM_NUMBER})

        reader = Mock()
        reader.read.return_value = ''
        urlopen.return_value = reader

        fobj = file_download.download_from_metadata(metadata)
        urlopen.assert_called_with(DOWNLOAD_URL, expected_params)
        self.assertTrue(fobj is reader)

    @patch('urllib2.urlopen')
    def test_download_from_metadata_not_cloud(self, urlopen):
        metadata = {'download_url': DOWNLOAD_URL,
                    'is_cloud': False,
                    'random_number': RANDOM_NUMBER,
                    'filename': FILENAME}

        reader = Mock()
        reader.read.return_value = ''
        urlopen.return_value = reader

        fobj = file_download.download_from_metadata(metadata)
        urlopen.assert_called_with(DOWNLOAD_URL)
        self.assertTrue(fobj is reader)
