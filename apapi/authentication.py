# -*- coding: utf-8 -*-
"""
apapi.authentication
~~~~~~~~~~~~~~~~
This module provides an AnaplanAuth object to use for requests authentication
"""

from requests.auth import AuthBase


class AnaplanAuth(AuthBase):
    """Allows to easily use Anaplan token for authentication"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = self.token
        return r