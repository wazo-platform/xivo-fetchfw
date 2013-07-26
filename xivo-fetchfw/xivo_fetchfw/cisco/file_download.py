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

import urllib
import os

from xivo_fetchfw.cisco.errors import DownloadError

BUFFER = 1024 * 1024


def download_from_metadata(metadata, location):
    if metadata['is_cloud']:
        params = urllib.urlencode({'X-Authentication-Control': metadata['random_number']})
        reader = urllib.urlopen(metadata['download_url'], params)
    else:
        reader = urllib.urlopen(metadata['download_url'])

    if reader.getcode() >= 400:
        raise DownloadError('HTTP Status: %s' % reader.getcode())

    path = os.path.join(location, metadata['filename'])
    with open(path, 'wb') as writer:
        data = reader.read(BUFFER)
        while data:
            writer.write(data)
            data = reader.read(BUFFER)
