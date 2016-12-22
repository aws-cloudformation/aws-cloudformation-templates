# -*- coding: utf-8 -*-
#
# Copyright 2010-2015 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Import from the future
from __future__ import absolute_import

# Low level API
from _pygit2 import *

# High level API
from .blame import Blame, BlameHunk
from .config import Config
from .credentials import *
from .errors import check_error, Passthrough
from .ffi import ffi, C
from .index import Index, IndexEntry
from .remote import Remote, RemoteCallbacks, get_credentials
from .repository import Repository
from .settings import Settings
from .submodule import Submodule
from .utils import to_bytes, to_str
from ._build import __version__


# Features
features = C.git_libgit2_features()
GIT_FEATURE_THREADS = C.GIT_FEATURE_THREADS
GIT_FEATURE_HTTPS = C.GIT_FEATURE_HTTPS
GIT_FEATURE_SSH = C.GIT_FEATURE_SSH

# GIT_REPOSITORY_INIT_*
GIT_REPOSITORY_INIT_OPTIONS_VERSION = C.GIT_REPOSITORY_INIT_OPTIONS_VERSION
GIT_REPOSITORY_INIT_BARE = C.GIT_REPOSITORY_INIT_BARE
GIT_REPOSITORY_INIT_NO_REINIT = C.GIT_REPOSITORY_INIT_NO_REINIT
GIT_REPOSITORY_INIT_NO_DOTGIT_DIR = C.GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
GIT_REPOSITORY_INIT_MKDIR = C.GIT_REPOSITORY_INIT_MKDIR
GIT_REPOSITORY_INIT_MKPATH = C.GIT_REPOSITORY_INIT_MKPATH
GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE = C.GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE
GIT_REPOSITORY_INIT_RELATIVE_GITLINK = C.GIT_REPOSITORY_INIT_RELATIVE_GITLINK
GIT_REPOSITORY_INIT_SHARED_UMASK = C.GIT_REPOSITORY_INIT_SHARED_UMASK
GIT_REPOSITORY_INIT_SHARED_GROUP = C.GIT_REPOSITORY_INIT_SHARED_GROUP
GIT_REPOSITORY_INIT_SHARED_ALL = C.GIT_REPOSITORY_INIT_SHARED_ALL

# GIT_ATTR_CHECK_*
GIT_ATTR_CHECK_FILE_THEN_INDEX = C.GIT_ATTR_CHECK_FILE_THEN_INDEX
GIT_ATTR_CHECK_INDEX_THEN_FILE = C.GIT_ATTR_CHECK_INDEX_THEN_FILE
GIT_ATTR_CHECK_INDEX_ONLY      = C.GIT_ATTR_CHECK_INDEX_ONLY
GIT_ATTR_CHECK_NO_SYSTEM       = C.GIT_ATTR_CHECK_NO_SYSTEM


def init_repository(path, bare=False,
                    flags=GIT_REPOSITORY_INIT_MKPATH,
                    mode=0,
                    workdir_path=None,
                    description=None,
                    template_path=None,
                    initial_head=None,
                    origin_url=None):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.

    The *flags* may be a combination of:

    - GIT_REPOSITORY_INIT_BARE (overriden by the *bare* parameter)
    - GIT_REPOSITORY_INIT_NO_REINIT
    - GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
    - GIT_REPOSITORY_INIT_MKDIR
    - GIT_REPOSITORY_INIT_MKPATH (set by default)
    - GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE

    The *mode* parameter may be any of GIT_REPOSITORY_SHARED_UMASK (default),
    GIT_REPOSITORY_SHARED_GROUP or GIT_REPOSITORY_INIT_SHARED_ALL, or a custom
    value.

    The *workdir_path*, *description*, *template_path*, *initial_head* and
    *origin_url* are all strings.

    See libgit2's documentation on git_repository_init_ext for further details.
    """
    # Pre-process input parameters
    if bare:
        flags |= GIT_REPOSITORY_INIT_BARE

    # Options
    options = ffi.new('git_repository_init_options *')
    C.git_repository_init_init_options(options,
                                       GIT_REPOSITORY_INIT_OPTIONS_VERSION)
    options.flags = flags
    options.mode = mode

    if workdir_path:
        workdir_path_ref = ffi.new('char []', to_bytes(workdir_path))
        options.workdir_path = workdir_path_ref

    if description:
        description_ref = ffi.new('char []', to_bytes(description))
        options.description = description_ref

    if template_path:
        template_path_ref = ffi.new('char []', to_bytes(template_path))
        options.template_path = template_path_ref

    if initial_head:
        initial_head_ref = ffi.new('char []', to_bytes(initial_head))
        options.initial_head = initial_head_ref

    if origin_url:
        origin_url_ref = ffi.new('char []', to_bytes(origin_url))
        options.origin_url = origin_url_ref

    # Call
    crepository = ffi.new('git_repository **')
    err = C.git_repository_init_ext(crepository, to_bytes(path), options)
    check_error(err)

    # Ok
    return Repository(to_str(path))

@ffi.callback('int (*git_repository_create_cb)(git_repository **out,'
              'const char *path, int bare, void *payload)')
def _repository_create_cb(repo_out, path, bare, data):
    d = ffi.from_handle(data)
    try:
        repository = d['repository_cb'](ffi.string(path), bare != 0)
        # we no longer own the C object
        repository._disown()
        repo_out[0] = repository._repo
    except Exception as e:
        d['exception'] = e
        return C.GIT_EUSER

    return 0

@ffi.callback('int (*git_remote_create_cb)(git_remote **out, git_repository *repo,'
              'const char *name, const char *url, void *payload)')
def _remote_create_cb(remote_out, repo, name, url, data):
    d = ffi.from_handle(data)
    try:
        remote = d['remote_cb'](Repository._from_c(repo, False), ffi.string(name), ffi.string(url))
        remote_out[0] = remote._remote
        # we no longer own the C object
        remote._remote = ffi.NULL
    except Exception as e:
        d['exception'] = e
        return C.GIT_EUSER

    return 0

def clone_repository(
        url, path, bare=False, repository=None, remote=None,
        checkout_branch=None, callbacks=None):
    """Clones a new Git repository from *url* in the given *path*.

    Returns a Repository class pointing to the newly cloned repository.

    :param str url: URL of the repository to clone

    :param str path: Local path to clone into

    :param bool bare: Whether the local repository should be bare

    :param callable remote: Callback for the remote to use.

    :param callable repository: Callback for the repository to use.

    :param str checkout_branch: Branch to checkout after the
     clone. The default is to use the remote's default branch.

    :param RemoteCallbacks callbacks: object which implements the
     callbacks as methods.

    :rtype: Repository

    The repository callback has `(path, bare) -> Repository` as a
    signature. The Repository it returns will be used instead of
    creating a new one.

    The remote callback has `(Repository, name, url) -> Remote` as a
    signature. The Remote it returns will be used instead of the default
    one.

    The callbacks should be an object which inherits from
    `pyclass:RemoteCallbacks`.

    """

    opts = ffi.new('git_clone_options *')
    crepo = ffi.new('git_repository **')

    branch = checkout_branch or None

    # Data, let's use a dict as we don't really want much more
    d = {}
    d['repository_cb'] = repository
    d['remote_cb'] = remote
    d_handle = ffi.new_handle(d)

    # Perform the initialization with the version we compiled
    C.git_clone_init_options(opts, C.GIT_CLONE_OPTIONS_VERSION)

    # We need to keep the ref alive ourselves
    checkout_branch_ref = None
    if branch:
        checkout_branch_ref = ffi.new('char []', to_bytes(branch))
        opts.checkout_branch = checkout_branch_ref

    if repository:
        opts.repository_cb = _repository_create_cb
        opts.repository_cb_payload = d_handle

    if remote:
        opts.remote_cb = _remote_create_cb
        opts.remote_cb_payload = d_handle


    opts.bare = bare

    if callbacks is None:
        callbacks = RemoteCallbacks()

    callbacks._fill_fetch_options(opts.fetch_opts)

    err = C.git_clone(crepo, to_bytes(url), to_bytes(path), opts)

    if 'exception' in d:
        raise d['exception']

    check_error(err)

    return Repository._from_c(crepo[0], owned=True)

settings = Settings()
