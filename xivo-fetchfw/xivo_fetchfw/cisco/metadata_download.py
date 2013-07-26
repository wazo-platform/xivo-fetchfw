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

import json
import urllib

from xivo_fetchfw.cisco.errors import MetadataError

DOWNLOAD_URL = "http://www.cisco.com/cisco/software/cart/service?a=downloadnow&imageGuId=%s&sa=&rnp=&k9=&eula=&atc=N&flowid=%s&config=&hAcl="


def download_metadata(guid, flowid, opener):
    url = DOWNLOAD_URL % (guid, flowid)
    reader = opener.open(url)

    metadata = _decode_metadata(reader.read())

    is_cloud = _extract_is_cloud(metadata)
    download_url = _extract_download_url(metadata)
    random_number = _extract_random_number(metadata)

    return {
        'download_url': download_url,
        'is_cloud': is_cloud,
        'random_number': random_number,
        'filename': metadata['fileName'],
    }


def _decode_metadata(raw_metadata):
    try:
        base_metadata = json.loads(raw_metadata)
    except ValueError:
        raise MetadataError('could not decode metadata (%s)' % raw_metadata)

    if 'dwldValidationSerResponse' not in base_metadata:
        raise MetadataError('missing property dwldValidationSerResponse in metadata')

    return base_metadata['dwldValidationSerResponse']


def _extract_is_cloud(metadata):
    urlinfo = _extract_url_info(metadata)
    is_cloud = urlinfo['isCloud']
    return is_cloud == 'Y'


def _extract_url_info(metadata):
    urllist = metadata.get('dwldURL', {}).get('downloadURLResponse', {}).get('urlList', [])
    if len(urllist) == 0:
        raise MetadataError('URL list not found in metadata')

    return urllist[0]


def _extract_download_url(metadata):
    urlinfo = _extract_url_info(metadata)
    download_url = urlinfo['downloadURL']
    return urllib.unquote(download_url)


def _extract_random_number(metadata):
    urlinfo = _extract_url_info(metadata)
    return urlinfo['randomNumber']
