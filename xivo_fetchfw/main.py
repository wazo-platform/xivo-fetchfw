# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sys
from operator import itemgetter
from xivo_fetchfw import cli, config, download, package, params, storage, util
from xivo_fetchfw import commands

logger = logging.getLogger('xivo-fetchfw')


def main():
    _init_logging()
    try:
        commands.execute_command(_XivoFetchfwCommand())
    except cli.UserCancellationError:
        pass
    except util.FetchfwError as e:
        print("error:", e, file=sys.stderr)
        logger.debug('Stack trace:', exc_info=True)
        sys.exit(1)
    except Exception as e:
        print("Unexpected exception:", e, file=sys.stderr)
        logger.debug('Stack trace:', exc_info=True)
        sys.exit(1)


def _init_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)


class _XivoFetchfwCommand(commands.AbstractCommand):
    def configure_parser(self, parser):
        parser.add_argument(
            '--config',
            default='/etc/xivo/xivo-fetchfw.conf',
            help='set an alternate configuration file',
        )
        parser.add_argument(
            '--debug', action='store_true', default=False, help='display debug messages'
        )
        parser.add_argument('--root', help='set the root directory')

    def configure_subcommands(self, subcommands):
        subcommands.add_subcommand(_InstallSubcommand('install'))
        subcommands.add_subcommand(_UpgradeSubcommand('upgrade'))
        subcommands.add_subcommand(_SearchSubcommand('search'))
        subcommands.add_subcommand(_RemoveSubcommand('remove'))

    def pre_execute(self, parsed_args):
        self._process_debug(parsed_args)
        self._process_config(parsed_args)
        self._process_root(parsed_args)
        self._create_pkg_mgr(parsed_args)

    def _process_debug(self, parsed_args):
        if parsed_args.debug:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

    def _process_config(self, parsed_args):
        config_filename = parsed_args.config
        try:
            config_dict = config.read_config(config_filename)
        except Exception as e:
            print(f"error: config file '{config_filename}': {e}", file=sys.stderr)
            logger.debug('Stack trace:', exc_info=True)
            sys.exit(1)
        else:
            parsed_args.config_dict = config_dict

    def _process_root(self, parsed_args):
        if not parsed_args.root:
            parsed_args.root = parsed_args.config_dict['general.root_dir']

    def _create_pkg_mgr(self, parsed_args):
        config_dict = parsed_args.config_dict
        proxies = params.filter_section(config_dict, 'proxy')
        downloaders = download.new_downloaders(proxies)
        global_vars = params.filter_section(config_dict, 'global_vars')
        able_pkg_sto, ed_pkg_sto = storage.new_pkg_storages(
            config_dict['general.db_dir'],
            config_dict['general.cache_dir'],
            downloaders,
            global_vars,
        )
        parsed_args.pkg_mgr = package.PackageManager(able_pkg_sto, ed_pkg_sto)


class _InstallSubcommand(commands.AbstractSubcommand):
    def configure_parser(self, parser):
        parser.add_argument('packages', nargs='+', help='package(s) to install')

    def execute(self, parsed_args):
        pkg_ids = parsed_args.packages
        pkg_mgr = parsed_args.pkg_mgr
        for pkg_id in pkg_ids:
            if (
                pkg_id in pkg_mgr.installed_pkg_sto
                and pkg_id in pkg_mgr.installable_pkg_sto
            ):
                installed_pkg = pkg_mgr.installed_pkg_sto[pkg_id]
                installed_version = installed_pkg.pkg_info['version']
                installable_version = pkg_mgr.installable_pkg_sto[pkg_id].pkg_info[
                    'version'
                ]
                cmp_result = util.cmp_version(installed_version, installable_version)
                if cmp_result == 0:
                    print(f"warning: {installed_pkg} is up to date -- reinstalling")
                else:
                    print(
                        f"error: {installed_pkg} is already installed",
                        file=sys.stderr,
                    )
                    sys.exit(1)
        ctrl_factory = cli.CliInstallerController.new_factory()
        pkg_mgr.install(pkg_ids, parsed_args.root, ctrl_factory)


class _UpgradeSubcommand(commands.AbstractSubcommand):
    def execute(self, parsed_args):
        pkg_mgr = parsed_args.pkg_mgr
        ctrl_factory = cli.CliUpgraderController.new_factory()
        pkg_mgr.upgrade(parsed_args.root, ctrl_factory)


class _SearchSubcommand(commands.AbstractSubcommand):
    def configure_parser(self, parser):
        parser.add_argument('pattern', nargs='?', help='search pattern')

    def execute(self, parsed_args):
        search_pattern = parsed_args.pattern
        pkg_mgr = parsed_args.pkg_mgr
        if not search_pattern:
            word = ''
        else:
            word = search_pattern.lower()
        for installable_pkg in _sorted_itervalues(pkg_mgr.installable_pkg_sto):
            pkg_id = installable_pkg.pkg_info['id']
            description = installable_pkg.pkg_info['description']
            if word in pkg_id.lower() or word in description.lower():
                if pkg_id in pkg_mgr.installed_pkg_sto:
                    installed_version = pkg_mgr.installed_pkg_sto[pkg_id].pkg_info[
                        'version'
                    ]
                    if installed_version != installable_pkg.pkg_info['version']:
                        print(installable_pkg, f"[installed: {installed_version}]")
                    else:
                        print(installable_pkg, "[installed]")
                else:
                    print(installable_pkg)
                print('   ', installable_pkg.pkg_info['description'])


def _sorted_itervalues(dict_):
    return list(map(itemgetter(1), sorted(dict_.items(), key=itemgetter(0))))


class _RemoveSubcommand(commands.AbstractSubcommand):
    def configure_parser(self, parser):
        parser.add_argument('packages', nargs='+', help='package(s) to remove')

    def execute(self, parsed_args):
        pkg_ids = parsed_args.packages
        pkg_mgr = parsed_args.pkg_mgr
        ctrl_factory = cli.CliUninstallerController.new_factory(recursive=True)
        pkg_mgr.uninstall(pkg_ids, parsed_args.root, ctrl_factory)
