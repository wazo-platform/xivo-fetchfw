# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import urllib


class ModelInfo(object):

    _CISCO_ROOT_URL = "http://www.cisco.com/cisco/software/release.html"

    def __init__(self, flow_id, url_params):
        self.flow_id = flow_id
        self.url_params = url_params

    def generate_url(self):
        return '%s?%s' % (self._CISCO_ROOT_URL, urllib.urlencode(self.url_params))
