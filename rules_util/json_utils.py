# -*- coding: utf-8 -*-
"""Utility / convenience functions for dealing with JSON."""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele'

import json
import error
from collections import OrderedDict

def parse_json(text):
    """Parse JSON into an OrderedDict."""
    try:
        return json.loads(text, object_pairs_hook=OrderedDict)
    except ValueError:
        raise error.UUJsonException('JSON file format error')
