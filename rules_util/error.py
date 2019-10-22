# -*- coding: utf-8 -*-
"""Common exception types."""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele, ...'

import re
from collections import OrderedDict

class UUException(Exception):
    """Generic Python rule exception.
       The base class for all Exceptions raised by UU rulesets.
    """


class UUFileSizeException(UUException):
    """File size limit exceeded"""


class UUMsiException(UUException):
    """Exception for microservice failure"""

    def __init__(self, message, msi_status, msi_code, msi_args, src_exception):
        super(UUMsiException, self).__init__(message)
        # Store msi result, if any.
        # These may be None when an msi aborts in an abnormal way.
        self.msi_status = msi_status
        self.msi_code = msi_code
        self.msi_args = msi_args
        self.src_exception = src_exception

    def __str__(self):
        if self.msi_status is not None:
            return '{}: error code {}'.format(self.message, self.msi_code)
        elif self.src_exception is not None:
            return '{}: iRODS error <{}>'.format(self.message, self.src_exception)
        else:
            return self.message


class JsonException(UUException):
    """Exception for unparsable JSON text"""
    # Python2's JSON lib raises ValueError on bad parses, which is ambiguous.
    # Use this exception (together with the functions below) instead.
    # (this can also ease transitions to python3, since python3's json already
    # uses a different, unambiguous exception type: json.JSONDecodeError)


class ApiError(UUException):
    """Error with descriptive (user-readable) message.

    Returned/raised by API functions to produce informative error output.
    """
    def __init__(self, name, message):
        self.name = name
        self.message = message
        super(ApiError, self).__init__(name)

    def __str__(self):
        return '{}: {}'.format(self.name, self.message)
    def as_dict(self):
        return OrderedDict([('error', self.name),
                            ('error_message', self.message)])
