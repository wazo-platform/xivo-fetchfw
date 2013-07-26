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

MODELS = {
    'SPA9X2': [('mdfid', '282414124'), ('flowid', '5285'), ('softwareid', '282463651'), ('release', '6.1.5a')],
    'SPA962': [('mdfid', '282414125'), ('flowid', '5286'), ('softwareid', '282463651'), ('release', '6.1.5a')],
    'SPA9X1': [('mdfid', '282414123'), ('flowid', '5284'), ('softwareid', '282463651'), ('release', '5.1.8')],
    'SPA901': [('mdfid', '282414119'), ('flowid', '5281'), ('softwareid', '282463651'), ('release', '4.1.17')],
    'SPA8000': [('mdfid', '282414110'), ('flowid', '5964'), ('softwareid', '282463187'), ('release', '6.1.11')],
    'PAP2T': [('mdfid', '282414114'), ('flowid', '5968'), ('softwareid', '282463187'), ('release', '5.1.6')],
    'SPA3102': [('mdfid', '282414112'), ('flowid', '5966'), ('softwareid', '282463187'), ('release', '5.2.13')],
    'SPA2102': [('mdfid', '282414111'), ('flowid', '5965'), ('softwareid', '282463187'), ('release', '5.2.13')],
    'SPA3X_5X': [('mdfid', '282724651'), ('flowid', '5301'), ('softwareid', '282463651'), ('release', '7.5.4')],
    'SPA525': [('mdfid', '282414147'), ('flowid', '5297'), ('softwareid', '282463651'), ('release', '7.5.4')],
    'LANG': [('mdfid', '282414147'), ('flowid', '5297'), ('softwareid', '282582477'), ('release', '7.5.4')],
    'SPA51X': [('mdfid', '284274685'), ('flowid', '33742'), ('softwareid', '282463651'), ('release', '7.5.4')],
    'SPA8800': [('mdfid', '282675423'), ('flowid', '22641'), ('softwareid', '282463645'), ('release', '6.1.7')],
}

CISCO_ROOT_URL = "http://www.cisco.com/cisco/software/release.html"


class NoInfoOnModelError(LookupError):

    def __init__(self, model):
        message = "no metadata on firmware for model %s" % model
        LookupError.__init__(self, message)


def generate_url(model):
    if model not in MODELS:
        raise NoInfoOnModelError(model)

    url_params = [p for p in MODELS[model] if p[0] != 'flowid']
    url = "%s?%s" % (CISCO_ROOT_URL, urllib.urlencode(url_params))
    return url


def flowid_for_model(model):
    filtered = [p[1] for p in MODELS[model] if p[0] == 'flowid']
    return filtered[0]
