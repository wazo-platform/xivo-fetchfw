# Copyright 2010-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import progressbar
from xivo_fetchfw.package import DefaultInstallerController, DefaultUninstallerController, \
    PackageError, DefaultUpgraderController
from xivo_fetchfw.download import ProgressBarHook

logger = logging.getLogger(__name__)


class UserCancellationError(PackageError):
    # Not an error per se, but raised when the user don't want to proceed
    pass


class CliInstallerController(DefaultInstallerController):
    def preprocess_raw_pkgs(self, raw_installable_pkgs):
        if not self._nodeps:
            print("resolving dependencies...")
        installable_pkgs = DefaultInstallerController.preprocess_raw_pkgs(
            self, raw_installable_pkgs)
        print("Targets (%d):" % len(installable_pkgs))
        for pkg in installable_pkgs:
            print("    ", pkg)
        print()
        return installable_pkgs

    def pre_download(self, remote_files):
        total_dl_size = sum(remote_file.size for remote_file in remote_files)
        print("Total Download Size:    %.2f MB" % (float(total_dl_size) / 1000 ** 2))
        print()
        rep = input("Proceed with installation? [Y/n] ")
        if rep and rep.lower() != 'y':
            raise UserCancellationError()

    def download_file(self, remote_file):
        widgets = [remote_file.filename,
                   ':    ',
                   progressbar.FileTransferSpeed(),
                   ' ',
                   progressbar.ETA(),
                   ' ',
                   progressbar.Bar(),
                   ' ',
                   progressbar.Percentage(),
                   ]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=remote_file.size)
        remote_file.download([ProgressBarHook(pbar)])

    def pre_install_pkg(self, installable_pkg):
        print("Installing %s..." % installable_pkg.pkg_info['id'])


class CliUninstallerController(DefaultUninstallerController):
    def pre_uninstall(self, installed_pkgs):
        print("Remove (%d):" % len(installed_pkgs))
        for pkg in installed_pkgs:
            print("    ", pkg)
        print()
        rep = input("Do you want to remove these packages? [Y/n] ")
        if rep and rep.lower() != 'y':
            raise UserCancellationError()

    def pre_uninstall_pkg(self, installed_pkg):
        print("Removing %s..." % installed_pkg.pkg_info['id'])


class CliUpgraderController(DefaultUpgraderController):
    _nothing_to_do = False

    def preprocess_upgrade_list(self, upgrade_list):
        if not self._nodeps:
            print("resolving dependencies...")
        installed_specs = DefaultUpgraderController.preprocess_upgrade_list(
            self, upgrade_list)
        if not installed_specs:
            print(" there is nothing to do")
            self._nothing_to_do = True
        else:
            installable_pkgs = []
            for installed_spec in installed_specs:
                installable_pkgs.append(installed_spec[1])
                installable_pkgs.extend(installed_spec[2])
            print("Targets (%d):" % len(installable_pkgs))
            for pkg in installable_pkgs:
                print("    ", pkg)
            print()
        return installed_specs

    def pre_download(self, remote_files):
        if self._nothing_to_do:
            return

        total_dl_size = sum(remote_file.size for remote_file in remote_files)
        print("Total Download Size:    %.2f MB" % (float(total_dl_size) / 1000 ** 2))
        print()
        rep = input("Proceed with upgrade? [Y/n] ")
        if rep and rep.lower() != 'y':
            raise UserCancellationError()

    def download_file(self, remote_file):
        widgets = [remote_file.filename,
                   ':    ',
                   progressbar.FileTransferSpeed(),
                   ' ',
                   progressbar.ETA(),
                   ' ',
                   progressbar.Bar(),
                   ' ',
                   progressbar.Percentage(),
                   ]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=remote_file.size)
        remote_file.download([ProgressBarHook(pbar)])

    def pre_upgrade_uninstall_pkg(self, installed_pkg):
        print("Removing %s..." % installed_pkg.pkg_info['id'])

    def pre_upgrade_install_pkg(self, installable_pkg):
        print("Installing %s..." % installable_pkg.pkg_info['id'])

    def pre_upgrade_pkg(self, installed_pkg):
        print("Upgrading %s..." % installed_pkg.pkg_info['id'])
