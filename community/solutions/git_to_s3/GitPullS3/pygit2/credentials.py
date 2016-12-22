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

from .ffi import C

GIT_CREDTYPE_USERPASS_PLAINTEXT = C.GIT_CREDTYPE_USERPASS_PLAINTEXT
GIT_CREDTYPE_SSH_KEY = C.GIT_CREDTYPE_SSH_KEY


class UserPass(object):
    """Username/Password credentials

    This is an object suitable for passing to a remote's credentials
    callback and for returning from said callback.
    """

    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def credential_type(self):
        return GIT_CREDTYPE_USERPASS_PLAINTEXT

    @property
    def credential_tuple(self):
        return (self._username, self._password)

    def __call__(self, _url, _username, _allowed):
        return self


class Keypair(object):
    """SSH key pair credentials

    This is an object suitable for passing to a remote's credentials
    callback and for returning from said callback.

    :param str username: the username being used to authenticate with the
        remote server
    :param str pubkey: the path to the user's public key file
    :param str privkey: the path to the user's private key file
    :param str passphrase: the password used to decrypt the private key file,
        or empty string if no passphrase is required.
    """

    def __init__(self, username, pubkey, privkey, passphrase):
        self._username = username
        self._pubkey = pubkey
        self._privkey = privkey
        self._passphrase = passphrase

    @property
    def credential_type(self):
        return GIT_CREDTYPE_SSH_KEY

    @property
    def credential_tuple(self):
        return (self._username, self._pubkey, self._privkey, self._passphrase)

    def __call__(self, _url, _username, _allowed):
        return self


class KeypairFromAgent(Keypair):
    def __init__(self, username):
        super(KeypairFromAgent, self).__init__(username, None, None, None)
