# Copyright 2011-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Module to transform configuration file to configuration data.

This is a bit of an experiment to create an easy, declarative way to declare
the valid format and options of an INI configuration file.

This module is not fetchfw specific, so it could be used by other projects if
it's found to be useful and not just a waste of time.

That said, look in fetchfw.config and fetchfw.conf to see examples on how
to use this module.

"""

import collections
from configparser import RawConfigParser


class ConfigSpec:
    """Represent a configuration file's specification."""

    NO_DEFAULT = object()
    MANDATORY = object()

    def __init__(self):
        # a dictionary where keys are param ids and values are tuple
        # (default value, fun). fun takes one argument, raw_value.
        self._params = {}
        # a dictionary where keys are section ids and values are fun. fun
        # takes two arguments, name and raw_value
        self._sections = {}
        # a dictionary where keys are template ids and values are dictionaries
        # which keys are options ids and value are tuple (default value, fun)
        self._dyn_params = collections.defaultdict(dict)
        self._unknown_section_hook = None
        self.add_param_decorator = self._create_param_decorator()
        self.add_dyn_param_decorator = self._create_dyn_param_decorator()
        self.add_section_decorator = self._create_section_decorator()
        self.set_unknown_section_hook_decorator = self._create_unknown_section_dec()

    def _create_param_decorator(self):
        def param_decorator(param_id, default=self.NO_DEFAULT):
            def aux(fun):
                self.add_param(param_id, default, fun)
                return fun

            return aux

        return param_decorator

    def _create_dyn_param_decorator(self):
        def dyn_param_decorator(template_id, option_id, default=self.NO_DEFAULT):
            def aux(fun):
                self.add_dyn_param(template_id, option_id, default, fun)
                return fun

            return aux

        return dyn_param_decorator

    def _create_section_decorator(self):
        def section_decorator(section_id):
            def aux(fun):
                self.add_section(section_id, fun)
                return fun

            return aux

        return section_decorator

    def _create_unknown_section_dec(self):
        def unknown_section_hook_decorator(fun):
            self.set_unknown_section_hook(fun)
            return fun

        return unknown_section_hook_decorator

    def add_param(self, param_id, default=NO_DEFAULT, fun=None):
        """
        param_id -- a parameter id, i.e. a section id concatenated with an
          option id. For example, "general.db_dir" is a valid param id.
        default -- the default value to set if the param is not present in
          the configuration file. If NO_DEFAULT, then the param is not set.
          If MANDATORY, then an error is raised if the parameter is missing.
        fun -- a function taking one argument, raw_value, and return
          the "cleaned" value. Can also be None.

        """
        if '.' not in param_id:
            raise ValueError(f'no dot character in param: {param_id}')
        if param_id in self._params:
            raise ValueError(f'param has already been specified: {param_id}')
        self._params[param_id] = (default, fun)

    def add_dyn_param(self, template_id, option_id, default=NO_DEFAULT, fun=None):
        """
        template_id -- an unique id for representing the unknown section
        fun -- a function taking one argument, raw_value, and return
          the "cleaned" value. Can also be None.

        Dynamic parameters are a way to process section which names is not
        known in advance. For this to work, you need to set a unknown section
        hook function that will examine each unknown section are return the
        correspondent template id.

        """
        template_dict = self._dyn_params[template_id]
        if option_id in template_dict:
            raise ValueError(
                f'dyn param already been specified: {template_id}.{option_id}'
            )
        template_dict[option_id] = (default, fun)

    def add_section(self, section_id, fun=None):
        """
        fun -- a function taking two arguments, option_id and raw_value, and return
          the "cleaned" value. Can also be None.

        """
        if '.' in section_id:
            raise ValueError(f'dot character in section: {section_id}')
        if section_id in self._sections:
            raise ValueError(f'section has already been specified: {section_id}')
        self._sections[section_id] = fun

    def set_unknown_section_hook(self, fun):
        """
        fun -- a function taking three arguments, config_dict, section_id,
          section_dict, and return the template id of the section or None.

        The unknown section hook is call after all known section have been
        processed, and it is call for every unknown section seen.

        """
        self._unknown_section_hook = fun

    def _process_param(self, param_id, raw_value):
        assert param_id in self._params
        fun = self._params[param_id][1]
        if fun is None:
            return raw_value
        else:
            return fun(raw_value)

    def _process_section(self, section_id, option_id, raw_value):
        assert section_id in self._sections
        fun = self._sections[section_id]
        if fun is None:
            return raw_value
        else:
            return fun(option_id, raw_value)

    def _add_default_and_check_mandatory(self, config_dict):
        for param_id, param_value in self._params.items():
            if param_id not in config_dict:
                default = param_value[0]
                if default is self.MANDATORY:
                    raise ValueError(f'missing parameter: {param_id}')
                elif default is self.NO_DEFAULT:
                    pass
                else:
                    config_dict[param_id] = default

    def read_config(self, config_parser):
        """Return a dictionary where keys are parameter ids and values are
        parameter values.

        """
        config_dict = {}
        unknown_sections = collections.defaultdict(dict)
        for section_id in config_parser.sections():
            for option_id, raw_value in config_parser.items(section_id):
                param_id = f"{section_id}.{option_id}"
                if param_id in self._params:
                    config_dict[param_id] = self._process_param(param_id, raw_value)
                elif section_id in self._sections:
                    config_dict[param_id] = self._process_section(
                        section_id, option_id, raw_value
                    )
                else:
                    unknown_sections[section_id][option_id] = raw_value
        self._add_default_and_check_mandatory(config_dict)

        # unknown section handling
        if unknown_sections:
            if self._unknown_section_hook:
                for section_id, section_dict in unknown_sections.items():
                    template_id = self._unknown_section_hook(
                        config_dict, section_id, section_dict
                    )
                    if template_id in self._dyn_params:
                        cur_dyn_params = self._dyn_params[template_id]
                        for option_id, raw_value in section_dict.items():
                            if option_id in cur_dyn_params:
                                fun = cur_dyn_params[option_id][1]
                                param_id = f'{section_id}.{option_id}'
                                if fun is None:
                                    config_dict[param_id] = raw_value
                                else:
                                    config_dict[param_id] = fun(raw_value)
                            else:
                                raise ValueError(
                                    f"unknown dynamic option {option_id} "
                                    f"for template {template_id}"
                                )
                        for option_id, (default, _) in cur_dyn_params.items():
                            param_id = f'{section_id}.{option_id}'
                            if param_id not in config_dict:
                                if default is self.MANDATORY:
                                    raise ValueError(
                                        f'missing dyn parameter: {param_id}'
                                    )
                                elif default is self.NO_DEFAULT:
                                    pass
                                else:
                                    config_dict[param_id] = default
                    else:
                        raise ValueError(
                            f"unknown template {template_id} returned for section {section_id}"
                        )
            else:
                raise ValueError(f"unknown sections: {list(unknown_sections.keys())}")
        return config_dict

    def read_config_from_filename(self, filename):
        config_parser = RawConfigParser()
        with open(filename) as f:
            config_parser.read_file(f)
        return self.read_config(config_parser)


def filter_section(config_dict, section_id):
    """Return a dictionary containing all the options of a given section.

    >>> d = {'foo.a': 1, 'foo.b': 2, 'bar.c': 3}
    >>> filter_section(d, 'foo')
    {'a': 1, 'b': 2}

    """
    if '.' in section_id:
        raise ValueError(f'dot character in section: {section_id}')
    result = {}
    dot_section_id = section_id + '.'
    dot_section_id_len = len(dot_section_id)
    for param_id, value in config_dict.items():
        if param_id.startswith(dot_section_id):
            result[param_id[dot_section_id_len:]] = value
    return result


_BOOL_TRUE = ['True', 'true']
_BOOL_FALSE = ['False', 'false']


def bool_(raw_value):
    """Return a bool from a string."""
    if raw_value in _BOOL_TRUE:
        return True
    elif raw_value in _BOOL_FALSE:
        return False
    else:
        raise ValueError(f'invalid boolean raw value "{raw_value}"')
