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

# Import from pygit2
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes, is_string


def assert_string(v, desc):
    if not is_string(v):
        raise TypeError("%s must be a string" % desc)


class ConfigIterator(object):

    def __init__(self, config, ptr):
        self._iter = ptr
        self._config = config

    def __del__(self):
        C.git_config_iterator_free(self._iter)

    def __iter__(self):
        return self

    def _next_entry(self):
        centry = ffi.new('git_config_entry **')
        err = C.git_config_next(centry, self._iter)
        check_error(err)

        return centry[0]

    def next(self):
        return self.__next__()

    def __next__(self):
        entry = self._next_entry()
        return ffi.string(entry.name).decode('utf-8')


class ConfigMultivarIterator(ConfigIterator):
    def __next__(self):
        entry = self._next_entry()
        return ffi.string(entry.value).decode('utf-8')


class Config(object):
    """Git configuration management"""

    def __init__(self, path=None):
        cconfig = ffi.new('git_config **')

        if not path:
            err = C.git_config_new(cconfig)
        else:
            assert_string(path, "path")
            err = C.git_config_open_ondisk(cconfig, to_bytes(path))

        check_error(err, True)
        self._config = cconfig[0]

    @classmethod
    def from_c(cls, repo, ptr):
        config = cls.__new__(cls)
        config._repo = repo
        config._config = ptr

        return config

    def __del__(self):
        C.git_config_free(self._config)

    def _get(self, key):
        assert_string(key, "key")

        entry = ffi.new('git_config_entry **')
        err = C.git_config_get_entry(entry, self._config, to_bytes(key))

        return err, ConfigEntry._from_c(entry[0])

    def _get_entry(self, key):
        err, entry = self._get(key)

        if err == C.GIT_ENOTFOUND:
            raise KeyError(key)

        check_error(err)
        return entry

    def __contains__(self, key):
        err, cstr = self._get(key)

        if err == C.GIT_ENOTFOUND:
            return False

        check_error(err)

        return True

    def __getitem__(self, key):
        entry = self._get_entry(key)

        return ffi.string(entry.value).decode('utf-8')

    def __setitem__(self, key, value):
        assert_string(key, "key")

        err = 0
        if isinstance(value, bool):
            err = C.git_config_set_bool(self._config, to_bytes(key), value)
        elif isinstance(value, int):
            err = C.git_config_set_int64(self._config, to_bytes(key), value)
        else:
            err = C.git_config_set_string(self._config, to_bytes(key),
                                          to_bytes(value))

        check_error(err)

    def __delitem__(self, key):
        assert_string(key, "key")

        err = C.git_config_delete_entry(self._config, to_bytes(key))
        check_error(err)

    def __iter__(self):
        citer = ffi.new('git_config_iterator **')
        err = C.git_config_iterator_new(citer, self._config)
        check_error(err)

        return ConfigIterator(self, citer[0])

    def get_multivar(self, name, regex=None):
        """Get each value of a multivar ''name'' as a list of strings.

        The optional ''regex'' parameter is expected to be a regular expression
        to filter the variables we're interested in.
        """
        assert_string(name, "name")

        citer = ffi.new('git_config_iterator **')
        err = C.git_config_multivar_iterator_new(citer, self._config,
                                                 to_bytes(name),
                                                 to_bytes(regex))
        check_error(err)

        return ConfigMultivarIterator(self, citer[0])

    def set_multivar(self, name, regex, value):
        """Set a multivar ''name'' to ''value''. ''regexp'' is a regular
        expression to indicate which values to replace.
        """
        assert_string(name, "name")
        assert_string(regex, "regex")
        assert_string(value, "value")

        err = C.git_config_set_multivar(self._config, to_bytes(name),
                                        to_bytes(regex), to_bytes(value))
        check_error(err)

    def get_bool(self, key):
        """Look up *key* and parse its value as a boolean as per the git-config
        rules. Return a boolean value (True or False).

        Truthy values are: 'true', 1, 'on' or 'yes'. Falsy values are: 'false',
        0, 'off' and 'no'
        """

        entry = self._get_entry(key)
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, entry.value)
        check_error(err)

        return res[0] != 0

    def get_int(self, key):
        """Look up *key* and parse its value as an integer as per the git-config
        rules. Return an integer.

        A value can have a suffix 'k', 'm' or 'g' which stand for 'kilo',
        'mega' and 'giga' respectively.
        """

        entry = self._get_entry(key)
        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, entry.value)
        check_error(err)

        return res[0]

    def add_file(self, path, level=0, force=0):
        """Add a config file instance to an existing config."""

        err = C.git_config_add_file_ondisk(self._config, to_bytes(path), level,
                                           force)
        check_error(err)

    def snapshot(self):
        """Create a snapshot from this Config object.

        This means that looking up multiple values will use the same version
        of the configuration files.
        """
        ccfg = ffi.new('git_config **')
        err = C.git_config_snapshot(ccfg, self._config)
        check_error(err)

        return Config.from_c(self._repo, ccfg[0])

    #
    # Methods to parse a string according to the git-config rules
    #

    @staticmethod
    def parse_bool(text):
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, to_bytes(text))
        check_error(err)

        return res[0] != 0

    @staticmethod
    def parse_int(text):
        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, to_bytes(text))
        check_error(err)

        return res[0]

    #
    # Static methods to get specialized version of the config
    #

    @staticmethod
    def _from_found_config(fn):
        buf = ffi.new('git_buf *', (ffi.NULL, 0))
        err = fn(buf)
        check_error(err, True)
        cpath = ffi.string(buf.ptr).decode()
        C.git_buf_free(buf)

        return Config(cpath)

    @staticmethod
    def get_system_config():
        """Return a <Config> object representing the system configuration file.
        """
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config():
        """Return a <Config> object representing the global configuration file.
        """
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config():
        """Return a <Config> object representing the global configuration file.
        """
        return Config._from_found_config(C.git_config_find_xdg)

class ConfigEntry(object):
    """An entry in a configuation object
    """

    @classmethod
    def _from_c(cls, ptr):
        entry = cls.__new__(cls)
        entry._entry = ptr
        return entry

    def __del__(self):
        C.git_config_entry_free(self._entry)

    @property
    def value(self):
        return self._entry.value
