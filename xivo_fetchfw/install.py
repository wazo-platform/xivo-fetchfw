# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import contextlib
import glob
import itertools
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from fnmatch import fnmatch

from xivo_fetchfw.util import FetchfwError

logger = logging.getLogger(__name__)


class InstallationError(FetchfwError):
    pass


class InstallationGraphError(InstallationError):
    pass


class _InstallationProcess:
    def __init__(self, sources, filters, dir=None):
        self._sources = sources
        self._filters = filters
        self._dir = dir
        self._executed = False
        self._need_cleanup = False
        self._base_dir = None

    def execute(self):
        """Execute the installation.

        Return the directory (subdirectory of dir) which contains the result
        of the installation process.

        """
        if self._executed:
            raise Exception('Installation process already executed')
        self._base_dir = tempfile.mkdtemp(dir=self._dir)
        req_map = self._build_requirement_map()

        sources = self._sources
        filters = self._filters
        result_dir, input_dirs, output_dirs = self._create_directories_map(req_map)
        try:
            for node_id in self._create_execution_plan(req_map):
                if node_id in sources:
                    source_obj = sources[node_id]
                    output_dir = output_dirs[node_id]
                    logger.debug("Executing source node %s", node_id)
                    source_obj.pull(output_dir)
                else:
                    assert node_id in filters
                    filter_obj = filters[node_id][0]
                    input_dir = input_dirs[node_id]
                    output_dir = output_dirs[node_id]
                    logger.debug("Executing filter node %s", node_id)
                    filter_obj.apply(input_dir, output_dir)
        except Exception:
            logger.error(
                "Error during execution of installation manager", exc_info=True
            )
            try:
                raise
            finally:
                shutil.rmtree(self._base_dir, True)
        else:
            self._executed = True
            self._need_cleanup = True
            return result_dir

    def _build_requirement_map(self):
        # Return a 'requirement map', i.e. a dictionary which keys are node id
        # and values are node id that depends on the key
        req_map = {
            node_id: [] for node_id in itertools.chain(self._sources, self._filters)
        }
        for filter_id, (_, filter_dependency) in self._filters.items():
            req_map[filter_dependency].append(filter_id)
        return req_map

    def _create_directories_map(self, req_map):
        # note that self._base_dir must have been set
        result_dir = os.path.join(self._base_dir, 'result')
        os.mkdir(result_dir)
        input_dirs = {}
        output_dirs = {}
        for node_id, requirements in req_map.items():
            if not requirements:
                # terminal node
                output_dirs[node_id] = result_dir
            else:
                # non-terminal node
                cur_dir = os.path.join(self._base_dir, 'node_' + node_id)
                os.mkdir(cur_dir)
                output_dirs[node_id] = cur_dir
                for requirement in requirements:
                    input_dirs[requirement] = cur_dir
        return result_dir, input_dirs, output_dirs

    def _create_execution_plan(self, req_map):
        # Return a iterator which gives a valid order of execution of nodes
        # The algorithm is correct since each filter has 1 and exactly 1 dependency
        deque = collections.deque(self._sources)
        while deque:
            node_id = deque.popleft()
            yield node_id
            for requirement in req_map[node_id]:
                if requirement not in deque:
                    deque.append(requirement)

    def cleanup(self):
        """Remove all files and directory created during the installation.

        Note that this includes the files in the result directory.

        It is safe to call this method even if the install process has not
        been executed or to call this method more than once.

        """
        if self._need_cleanup:
            shutil.rmtree(self._base_dir, True)
            self._need_cleanup = False


class InstallationManager:
    """An installation manager..."""

    def __init__(self, installation_graph):
        r"""Build an InstallationManager.

        Installation_graph is a dictionary, for example:
          {'filters':
              {'ZipFilter1': (<ZipFilter object>, 'TarFilter1'),
               'TarFilter1': (<TarFilter object>, 'FilesystemLinkSource'),
              },
           'sources':
              {'FilesystemLinkSource1': <FilesystemLinkSource object>}
          }

        Note that node id MUST match the regex \w+.

        A filter is an object with a 'apply(src_directory, dst_directory)' method.
        A source is an object with a 'pull(dst_directory)' method.

        Raise an InstallationGraphError if the installation graph is invalid.

        """
        self._sources = installation_graph['sources']
        self._filters = installation_graph['filters']
        self._check_installation_graph_validity()

    def _check_installation_graph_validity(self):
        # Check if the installation graph is valid, if not, raise an InstallationError.
        self._check_nodes_id_are_unique()
        self._check_filters_depend_on_valid_node()
        self._check_no_useless_source()
        self._check_is_acyclic()

    def _check_nodes_id_are_unique(self):
        common_ids = set(self._sources).intersection(self._filters)
        if common_ids:
            raise InstallationGraphError(
                f"these IDs are shared by both a source and a filter: {common_ids}"
            )

    def _check_filters_depend_on_valid_node(self):
        # Check that there's no unknown identifier in the installation graph, i.e. raise an
        # exception if there's a filter such that it depends on an unknown node.
        sources = self._sources
        filters = self._filters
        for filter_id, filter_value in filters.items():
            node_dependency = filter_value[1]
            if node_dependency not in filters and node_dependency not in sources:
                raise InstallationGraphError(
                    f"filter '{filter_id}' depends on unknown filter/source '{node_dependency}'"
                )

    def _check_no_useless_source(self):
        # Check if every source participates in the installation process, i.e. raise an exception
        # if there's a source such that no other filter depend on it.
        dependencies = (v[1] for v in self._filters.values())
        unused_sources = set(self._sources).difference(dependencies)
        if unused_sources:
            raise InstallationGraphError(
                f"these sources doesn't participate in the installation: {unused_sources}"
            )

    def _check_is_acyclic(self):
        # Check that the installation graph is acyclic
        sources = self._sources
        filters = self._filters
        visited = set()
        for node_id in filters:
            if node_id not in visited:
                currently_visited = {node_id}
                while True:
                    next_node_id = filters[node_id][1]
                    if next_node_id in sources:
                        break
                    if next_node_id in currently_visited:
                        raise InstallationGraphError(
                            "a cycle in the installation graph has been detected"
                        )
                    currently_visited.add(next_node_id)
                    node_id = next_node_id
                visited.update(currently_visited)

    def new_installation_process(self, dir=None):
        """Return an installation process instance, i.e. an object with an
        "execute" and "cleanup" method.

        See _InstallationProcess for more info on these methods.

        Temporaries directory and files will be created in subdirectories of
        dir, which can be None, in the case the default system temporary
        directory will be used.

        """
        return _InstallationProcess(self._sources, self._filters, dir)


class _GlobHelper:
    """The python glob module works only with the notion of the current directory.
    This class is used to facilitate the application of one or more glob patterns
    inside arbitrary directories.

    """

    def __init__(self, pathnames, error_on_no_matches=True):
        """pathnames can be either a single path name or an iterable of path names."""
        if isinstance(pathnames, str):
            self._pathnames = [os.path.normpath(pathnames)]
        else:
            self._pathnames = [os.path.normpath(pathname) for pathname in pathnames]
        for pathname in self._pathnames:
            if os.path.isabs(pathname):
                raise ValueError(f"path name '{pathname}' is an absolute path")
            if pathname.startswith(os.pardir):
                raise ValueError(
                    f"path name '{pathname}' makes reference to the parent directory"
                )
        self._error_on_no_matches = error_on_no_matches

    def glob_in_dir(self, src_directory):
        return list(self.iglob_in_dir(src_directory))

    def iglob_in_dir(self, src_directory):
        """Apply the glob patterns in src_directory and return an iterator over
        each file matched.

        """
        no_matches = True
        for rel_pathname in self._pathnames:
            abs_pathname = os.path.join(src_directory, rel_pathname)
            for globbed_abs_pathname in glob.iglob(abs_pathname):
                no_matches = False
                yield globbed_abs_pathname
        if no_matches and self._error_on_no_matches:
            raise InstallationError(
                f"the glob patterns {self._pathnames} did not "
                f"match anything in directory '{src_directory}'"
            )


class FilesystemLinkSource:
    """A source which create symlink of existing files to the destination
    directory.

    You should be careful if you plan on using this source with directories,
    i.e. you might be looking for trouble if you are creating links to parent
    directories of the destination directory.

    """

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        if isinstance(pathnames, str):
            self._pathnames = [pathnames]
        else:
            self._pathnames = list(pathnames)

    def pull(self, dst_directory):
        for pathname in self._pathnames:
            for globbed_pathname in glob.iglob(pathname):
                os.symlink(
                    globbed_pathname,
                    os.path.join(dst_directory, os.path.basename(globbed_pathname)),
                )


class NonGlobbingFilesystemLinkSource:
    def __init__(self, pathnames):
        """
        pathnames -- a single pathname or an iterator over multiple pathnames

        """
        if isinstance(pathnames, str):
            self._pathnames = [pathnames]
        else:
            self._pathnames = list(pathnames)

    def pull(self, dst_directory):
        for pathname in self._pathnames:
            # note that we check if pathname really exist so we can easily
            # detect human error, that said it's still possible that the file
            # be removed during execution
            if not os.path.exists(pathname):
                raise InstallationError(f'path doesn\'t exist: {pathname}')
            os.symlink(
                pathname, os.path.join(dst_directory, os.path.basename(pathname))
            )


class FilesystemCopySource:
    """A cleaner alternative to FilesystemLinkSource if you are worried about
    race condition, side effects, etc.

    """

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        if isinstance(pathnames, str):
            self._pathnames = [pathnames]
        else:
            self._pathnames = list(pathnames)

    def pull(self, dst_directory):
        for pathname in self._pathnames:
            for globbed_pathname in glob.iglob(pathname):
                dst_pathname = os.path.join(
                    dst_directory, os.path.basename(globbed_pathname)
                )
                if os.path.isdir(globbed_pathname):
                    shutil.copytree(globbed_pathname, dst_pathname)
                else:
                    shutil.copy(globbed_pathname, dst_pathname)


class NullSource:
    """A source that add nothing to the destination directory.

    Mostly useful for testing purposes.

    """

    def pull(self, dst_directory):
        pass


class ZipFilter:
    """A filter who transform a directory containing zip files to a directory containing
    the content of these zip files.

    """

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        self._glob_helper = _GlobHelper(pathnames)

    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            with contextlib.closing(zipfile.ZipFile(pathname, 'r')) as zf:
                zf.extractall(dst_directory)


class TarFilter:
    """A filter who transform a directory containing tar files to a directory containing
    the content of these tar files. The tar files can be either uncompressed, gzipped
    or bz2-ipped.

    """

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        self._glob_helper = _GlobHelper(pathnames)

    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            with contextlib.closing(tarfile.open(pathname)) as tf:
                tf.extractall(dst_directory)


class RarFilter:
    """A filter who transform a directory containing rar files to a directory
    containing the content of these rar files.

    Note that it depends on the "unrar" executable to be present on the host
    system. On Debian squeeze, this executable is found in the "unrar"
    package (non-free version).

    """

    _CMD_PREFIX = ['unrar', 'e', '-idq', '-y']

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        self._glob_helper = _GlobHelper(pathnames)

    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            cmd = self._CMD_PREFIX + [pathname, dst_directory]
            logger.debug('Executing external command: %s', cmd)
            retcode = subprocess.call(cmd)
            if retcode:
                raise InstallationError(f'unrar returned status code {retcode}')


class Filter7z:
    """A filter who transform a directory containing 7z files to a directory
    containing the content of these 7z files.

    Note that it depends on the "7zr" executable to be present on the host
    system. On Debian squeeze, this executable is found in the "p7zip" package.

    Also, note that the 7zr has a somehow weird behaviour when specifying an
    output directory, files inside directory of the archive will be all
    extracted in the same base directory.

    This class is not named '7zFilter' because this is an invalid python
    identifier.

    """

    _CMD_PREFIX = ['7zr', 'e', '-bd']

    def __init__(self, pathnames):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns

        """
        self._glob_helper = _GlobHelper(pathnames)

    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            cmd = self._CMD_PREFIX + [f'-o{dst_directory}', pathname]
            # there's no "quiet" option for 7zr, so we redirect stdout to /dev/null
            with open(os.devnull, 'wb') as devnull_fobj:
                logger.debug('Executing external command: %s', cmd)
                retcode = subprocess.call(cmd, stdout=devnull_fobj)
            if retcode:
                raise InstallationError(f'7zr returned status code {retcode}')


class CiscoUnsignFilter:
    """A filter who transform a directory containing a Cisco-signed gzip file to a directory
    containing the gzipped file inside the signed file.

    """

    _BUF_SIZE = 512
    _GZIP_MAGIC_NUMBER = (
        b'\x1f\x8b'  # see http://www.gzip.org/zlib/rfc-gzip.html#file-format
    )

    def __init__(self, signed_pathname, unsigned_pathname):
        """Note: signed_pathname can be a glob pattern, but when the pattern is expanded,
        it must match only ONE file or an error will be raised. This is for convenience, so
        that if you don't know the exact name of a file, you can still use a glob pattern to
        match it.

        """
        self._glob_helper = _GlobHelper(signed_pathname)
        self._unsigned_pathname = os.path.normpath(unsigned_pathname)
        if os.path.isabs(self._unsigned_pathname):
            raise ValueError(
                f"unsigned path name '{self._unsigned_pathname}' is an absolute path"
            )
        if self._unsigned_pathname.startswith(os.pardir):
            raise ValueError(
                f"unsigned path name '{self._unsigned_pathname}' "
                "makes reference to the parent directory"
            )

    def apply(self, src_directory, dst_directory):
        signed_pathnames = self._glob_helper.glob_in_dir(src_directory)
        if len(signed_pathnames) > 1:
            raise InstallationError(
                f"glob pattern matched {len(signed_pathnames)} files"
            )
        signed_pathname = signed_pathnames[0]
        with open(signed_pathname, 'rb') as sf:
            buf = sf.read(CiscoUnsignFilter._BUF_SIZE)
            index = buf.find(CiscoUnsignFilter._GZIP_MAGIC_NUMBER)
            if index == -1:
                raise InstallationError(
                    "Couldn't find gzip magic number in the signed file."
                )
            unsigned_filename = os.path.join(dst_directory, self._unsigned_pathname)
            with open(unsigned_filename, 'wb') as f:
                f.write(buf[index:])
                shutil.copyfileobj(sf, f)


class IncludeExcludeFilter:
    def __init__(self, filter_fun):
        """
        filter_fun -- a callable object taking two arguments, the first being
          the relative name of the file currently under test and the second
          being the absolute name of the file. The call returns true if the
          file is to be included in the destination directory, or false to
          exclude it.

        The relative name is relative to the source directory, i.e. if the
        source directory contains a directory named 'dir1' that contains a
        file named 'file1', the relative name for this file would be
        'dir1/file1'.

        Note that if false is returned for a file that is a directory, the
        filter_fun object won't be called for any files under this directory
        because it wouldn't make sense to include a file if you excluded the
        parent directory.

        That said, if true is returned for a directory, the files under this
        directory are not automatically included and the filter_fun will be
        called for every child files of this directory.

        """
        self._filter_fun = filter_fun

    def apply(self, src_directory, dst_directory):
        rel_dir_stack = [os.curdir]
        while rel_dir_stack:
            rel_current_dir = rel_dir_stack.pop()
            abs_current_dir = os.path.join(src_directory, rel_current_dir)
            for file in os.listdir(abs_current_dir):
                if rel_current_dir == os.curdir:
                    rel_file = file
                else:
                    rel_file = os.path.join(rel_current_dir, file)
                src_abs_file = os.path.join(src_directory, rel_file)
                if self._filter_fun(rel_file, src_abs_file):
                    dst_abs_file = os.path.join(dst_directory, rel_file)
                    if os.path.isdir(src_abs_file):
                        os.mkdir(dst_abs_file)
                        rel_dir_stack.append(rel_file)
                    else:
                        shutil.copy(src_abs_file, dst_abs_file)


def ExcludeFilter(pathnames):
    """A filter which excludes some files of the source directory from the destination
    directory. Excluded files can be either files, directories or both.

    Takes the following arguments:
      pathnames -- a single glob pattern or an iterator over multiple glob
        patterns

    """
    if isinstance(pathnames, str):
        pathnames = [pathnames]
    else:
        pathnames = list(pathnames)

    def filter_fun(rel_file, abs_file):
        for pathname in pathnames:
            if fnmatch(rel_file, pathname):
                return False
        return True

    return IncludeExcludeFilter(filter_fun)


def IncludeFilter(pathnames):
    """A filter which includes some files of the source directory from the destination
    directory. Included files can be either files, directories or both.

    Takes the following arguments:
      pathnames -- a single glob pattern or an iterator over multiple glob
        patterns

    """
    if isinstance(pathnames, str):
        pathnames = [pathnames]
    else:
        pathnames = list(pathnames)

    included_dirs = set()

    def filter_fun(rel_file, abs_file):
        # include rel_file if its a child of an already included directory
        rel_dirname = os.path.dirname(rel_file)
        if rel_dirname in included_dirs:
            if os.path.isdir(abs_file):
                included_dirs.add(rel_file)
            return True
        for pathname in pathnames:
            if fnmatch(rel_file, pathname):
                if os.path.isdir(abs_file):
                    included_dirs.add(rel_file)
                return True
        return False

    return IncludeExcludeFilter(filter_fun)


class CopyFilter:
    """A filter which copy one or more files or directories to a certain path
    in the destination directory.

    """

    def __init__(self, pathnames, dst):
        """
        pathnames -- a single glob pattern or an iterator over multiple glob
          patterns
        dst -- either a directory name, if it ends with '/', or else a file name.
          This must be explicit because the installer create any missing directory
          when copying files. This is a relative destination.

        """
        self._glob_helper = _GlobHelper(pathnames)
        self._dst = dst

    def apply(self, src_directory, dst_directory):
        dst_is_dir = self._dst.endswith('/')
        abs_dst = os.path.join(dst_directory, self._dst)
        try:
            if os.path.exists(abs_dst):
                if os.path.isdir(abs_dst) != dst_is_dir:
                    if dst_is_dir:
                        raise InstallationError(
                            "destination exists and is a file but should be a directory"
                        )
                    else:
                        raise InstallationError(
                            "destination exists and is a directory but should be a file"
                        )
            else:
                dirname = os.path.dirname(abs_dst)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            if dst_is_dir:
                self._apply_dir(src_directory, abs_dst)
            else:
                self._apply_file(src_directory, abs_dst)
        except OSError as e:
            logger.error("Error during execution of copy filter", exc_info=True)
            raise InstallationError(e)

    def _apply_dir(self, src_directory, abs_dst):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            if os.path.isdir(pathname):
                src_dir_name = os.path.basename(pathname)
                shutil.copytree(pathname, os.path.join(abs_dst, src_dir_name), True)
            else:
                shutil.copy(pathname, abs_dst)

    def _apply_file(self, src_directory, abs_dst):
        pathnames = self._glob_helper.glob_in_dir(src_directory)
        if len(pathnames) > 1:
            raise InstallationError(f"glob pattern matched {len(pathnames)} files")
        pathname = pathnames[0]
        shutil.copy(pathname, abs_dst)


class NullFilter:
    """A filter that add nothing to the destination directory.

    Mostly useful for testing purposes.

    """

    def apply(self, src_directory, dst_directory):
        pass
