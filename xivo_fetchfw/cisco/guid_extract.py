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

from BeautifulSoup import BeautifulSoup

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
    classes = tag['class'].split(' ')
    for classname in classes:
        if classname.startswith(PREFIX):
            return classname[len(PREFIX):]
    raise NoGuidFoundError()
