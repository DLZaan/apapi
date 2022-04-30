"""
apapi.authentication
~~~~~~~~~~~~~~~~
This module provides helper classes for authentication needs
"""
from enum import Enum

from requests.auth import AuthBase


class AnaplanAuth(AuthBase):
    """Allows to easily use Anaplan token for authentication"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = self.token
        return r


class AuthType(Enum):
    """Needed during initialization of connection to choose
    which authentication option should be used"""

    BASIC = "Basic"
    """Basic Authentication using username (email) and Anaplan password"""
    CERT = "CACertificate"
    """NOT IMPLEMENTED YET Certificate Authentication using S/MIME certificate"""
