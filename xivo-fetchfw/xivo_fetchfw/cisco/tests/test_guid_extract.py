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

from mock import patch, Mock
from xivo_fetchfw.cisco.guid_extract import NoGuidFoundError, GuidDownloadError
from xivo_fetchfw.cisco import guid_extract as extractor


class TestGuidExtract(unittest.TestCase):

    SAMPLE_DOWNLOAD_PAGE = "downloadpage.html"
    SAMPLE_GUID = "A9A12528CEACD186373D7463E1D03DD0D42E8DDE"

    def test_extract_from_html(self):
        html = self._html_from_sample_download_page()

        result = extractor.extract_from_html(html)

        self.assertEquals(self.SAMPLE_GUID, result)

    def _html_from_sample_download_page(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, self.SAMPLE_DOWNLOAD_PAGE)
        html = open(path).read()
        return html

    def test_extract_from_html_with_no_html(self):
        html = ''

        self.assertRaises(NoGuidFoundError, extractor.extract_from_html, html)

    def test_extract_from_html_no_button(self):
        html = """
        <html>
            <body>
                <p>Hello World</p>
            </body>
        </html>
        """

        self.assertRaises(NoGuidFoundError, extractor.extract_from_html, html)

    def test_extract_from_html_button_with_no_guid(self):
        html = """
        <html>
            <body>
                <input id="sdpriDownloadNow0" class="class1 class2 class3" />
            </body>
        </html>
        """

        self.assertRaises(NoGuidFoundError, extractor.extract_from_html, html)

    @patch('urllib.urlopen')
    def test_extract_from_url(self, urlopen_mock):
        url = "http://example.com"

        reader_mock = Mock()
        reader_mock.read.return_value = self._html_from_sample_download_page()
        urlopen_mock.return_value = reader_mock

        result = extractor.extract_from_url(url)

        self.assertEquals(self.SAMPLE_GUID, result)
        urlopen_mock.assert_called_once_with(url)

    @patch('urllib.urlopen')
    def test_extract_from_url_with_download_error(self, urlopen_mock):
        url = "http://example.com"

        reader_mock = Mock()
        reader_mock.read.side_effect = IOError()
        urlopen_mock.return_value = reader_mock

        self.assertRaises(GuidDownloadError, extractor.extract_from_url, url)
