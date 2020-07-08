# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from bs4 import BeautifulSoup

INPUT_ID = "sdpriDownloadNow0"
PREFIX = "sdpriDownloadNow"


class NoGuidFoundError(ValueError):

    def __init__(self):
        message = "no guid found on download page"
        ValueError.__init__(self, message)


def extract_from_url(url, opener):
    html = _download_html(url, opener)
    return extract_from_html(html)


def _download_html(url, opener):
    return opener.open(url).read()


def extract_from_html(html):
    soup = BeautifulSoup(html)
    tag = _find_guid_tag(soup)
    return _extract_guid_from_tag(tag)


def _find_guid_tag(soup):
    tag = soup.find('input', id=INPUT_ID)
    if not tag:
        raise NoGuidFoundError()
    return tag


def _extract_guid_from_tag(tag):
    for classname in tag['class']:
        if classname.startswith(PREFIX):
            return classname[len(PREFIX):]
    raise NoGuidFoundError()
