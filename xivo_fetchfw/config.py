# -*- coding: utf-8 -*-
# Copyright 2010-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import
from six.moves.configparser import RawConfigParser
from xivo_fetchfw.params import ConfigSpec


def _new_config_spec():
    cfg_spec = ConfigSpec()

    # [general] section definition
    cfg_spec.add_param('general.root_dir', default='/')
    cfg_spec.add_param('general.db_dir', default='/var/lib/xivo-fetchfw')
    cfg_spec.add_param('general.cache_dir', default='/var/cache/xivo-fetchfw')

    @cfg_spec.add_param_decorator('general.auth_sections', default=[])
    def _auth_sections_fun(raw_value):
        return raw_value.split()

    # [global_vars] section definition
    cfg_spec.add_section('global_vars')

    # [proxy] section definition
    cfg_spec.add_section('proxy')

    # dynamic [auth-section] definition (referenced by general.auth_sections)
    cfg_spec.add_dyn_param('auth-section', 'uri', default=ConfigSpec.MANDATORY)
    cfg_spec.add_dyn_param('auth-section', 'username', default=ConfigSpec.MANDATORY)
    cfg_spec.add_dyn_param('auth-section', 'password', default=ConfigSpec.MANDATORY)

    # unknown section hook for dynamic auth sections
    @cfg_spec.set_unknown_section_hook_decorator
    def _unknown_section_hook(config_dict, section_id, section_dict):
        if section_id in config_dict['general.auth_sections']:
            return 'auth-section'

    return cfg_spec

_CONFIG_SPEC = _new_config_spec()


def read_config(filename):
    config_parser = RawConfigParser()
    # case sensitive options (used for section 'global_vars')
    config_parser.optionxform = str
    with open(filename) as fobj:
        config_parser.readfp(fobj)
    return _CONFIG_SPEC.read_config(config_parser)
