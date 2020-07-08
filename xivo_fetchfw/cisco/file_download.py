# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import urllib


def download_from_metadata(metadata, opener):
    if metadata['is_cloud']:
        params = urllib.urlencode({'X-Authentication-Control': metadata['random_number']})
        reader = opener.open(metadata['download_url'], params)
    else:
        reader = opener.open(metadata['download_url'])

    return reader
