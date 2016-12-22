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

# Import from pygit2
from .ffi import ffi, C
from _pygit2 import GitError


value_errors = set([C.GIT_EEXISTS, C.GIT_EINVALIDSPEC, C.GIT_EEXISTS,
                    C.GIT_EAMBIGUOUS])

def check_error(err, io=False):
    if err >= 0:
        return

    # Error message
    giterr = C.giterr_last()
    if giterr != ffi.NULL:
        message = ffi.string(giterr.message).decode()
    else:
        message = "err %d (no message provided)" % err

    # Translate to Python errors
    if err in value_errors:
        raise ValueError(message)

    if err == C.GIT_ENOTFOUND:
        if io:
            raise IOError(message)

        raise KeyError(message)

    if err == C.GIT_EINVALIDSPEC:
        raise ValueError(message)

    if err == C.GIT_ITEROVER:
        raise StopIteration()

    # Generic Git error
    raise GitError(message)

# Indicate that we want libgit2 to pretend a function was not set
Passthrough = Exception("The function asked for pass-through")
