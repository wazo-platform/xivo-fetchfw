# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_fetchfw.cisco import metadata_download, guid_extract, file_download


def download_firmware(model_info, opener):
    url = model_info.generate_url()
    guid = _extract_guid(url, opener)
    return _download_firmware(guid, model_info.flow_id, opener)


def _extract_guid(url, opener):
    return guid_extract.extract_from_url(url, opener)


def _download_firmware(guid, flowid, opener):
    metadata = metadata_download.download_metadata(guid, flowid, opener)
    return file_download.download_from_metadata(metadata, opener)
