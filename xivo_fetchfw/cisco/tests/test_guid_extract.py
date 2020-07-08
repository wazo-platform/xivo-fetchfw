# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import os

from mock import Mock
from xivo_fetchfw.cisco.guid_extract import NoGuidFoundError
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

    def test_extract_from_url(self):
        url = "http://example.com"

        reader_mock = Mock()
        reader_mock.read.return_value = self._html_from_sample_download_page()
        opener = Mock()
        opener.open.return_value = reader_mock

        result = extractor.extract_from_url(url, opener)

        self.assertEquals(self.SAMPLE_GUID, result)
        opener.open.assert_called_once_with(url)
