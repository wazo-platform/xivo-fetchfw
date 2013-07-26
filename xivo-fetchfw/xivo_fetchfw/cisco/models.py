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


class ModelInfo(object):

    _CISCO_ROOT_URL = "http://www.cisco.com/cisco/software/release.html"

    def __init__(self, flow_id, url_params):
        self.flow_id = flow_id
        self.url_params = url_params

    def generate_url(self):
        return '%s?%s' % (self._CISCO_ROOT_URL, urllib.urlencode(self.url_params))
