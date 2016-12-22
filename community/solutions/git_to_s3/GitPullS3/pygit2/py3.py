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

# Import from pygit2
from .ffi import ffi


def to_bytes(s, encoding='utf-8', errors='strict'):
    if s == ffi.NULL or s is None:
        return ffi.NULL

    if isinstance(s, bytes):
        return s

    return s.encode(encoding, errors)


def is_string(s):
    return isinstance(s, str)


def to_str(s):
    if type(s) is str:
        return s

    if type(s) is bytes:
        return s.decode()

    raise TypeError('unexpected type "%s"' % repr(s))
