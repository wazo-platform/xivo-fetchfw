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

from xivo_fetchfw.cisco import models, metadata_download, guid_extract, file_download
from xivo_fetchfw.cisco.errors import DownloadError


def download_firmware(model, download_location):
    url = _url_for_model(model)
    guid = _extract_guid(url, model)
    flowid = _flowid_for_model(model)
    _download_firmware(guid, flowid, model, download_location)


def _url_for_model(model):
    return models.generate_url(model)


def _extract_guid(url, model):
    return guid_extract.extract_from_url(url)


def _flowid_for_model(model):
    return models.flowid_for_model(model)


def _download_firmware(guid, flowid, model, location):
    metadata = metadata_download.download_metadata(guid, flowid)
    try:
        file_download.download_from_metadata(metadata, location)
    except IOError:
        raise DownloadError(model)
