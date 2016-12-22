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
from __future__ import absolute_import, unicode_literals

from .errors import check_error
from .ffi import ffi, C

class Submodule(object):

    @classmethod
    def _from_c(cls, repo, cptr):
        subm = cls.__new__(cls)

        subm._repo = repo
        subm._subm = cptr

        return subm

    def __del__(self):
        C.git_submodule_free(self._subm)

    def open(self):
        """Open the repository for a submodule."""
        crepo = ffi.new('git_repository **')
        err = C.git_submodule_open(crepo, self._subm)
        check_error(err)

        return self._repo._from_c(crepo[0], True)

    @property
    def name(self):
        """Name of the submodule."""
        name = C.git_submodule_name(self._subm)
        return ffi.string(name).decode('utf-8')

    @property
    def path(self):
        """Path of the submodule."""
        path = C.git_submodule_path(self._subm)
        return ffi.string(path).decode('utf-8')

    @property
    def url(self):
        """URL of the submodule."""
        url = C.git_submodule_url(self._subm)
        return ffi.string(url).decode('utf-8')

    @property
    def branch(self):
        """Branch that is to be tracked by the submodule."""
        branch = C.git_submodule_branch(self._subm)
        return ffi.string(branch).decode('utf-8')
