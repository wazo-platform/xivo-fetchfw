# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


class MetadataError(ValueError):

    def __init__(self, message=''):
        message = "error while extracting download metadata. %s" % message
        ValueError.__init__(self, message)
