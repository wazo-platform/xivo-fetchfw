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

from xivo_fetchfw.cisco import metadata_download, guid_extract, file_download


def download_firmware(model_info, opener):
    url = model_info.generate_url()
    guid = _extract_guid(url, opener)
    flowid = model_info.flow_id
    return _download_firmware(guid, flowid, opener)


def _extract_guid(url, opener):
    return guid_extract.extract_from_url(url, opener)


def _download_firmware(guid, flowid, opener):
    metadata = metadata_download.download_metadata(guid, flowid, opener)
    return file_download.download_from_metadata(metadata, opener)
