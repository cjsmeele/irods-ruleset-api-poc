# -*- coding: utf-8 -*-
"""An example module within a ruleset.

This contains several API rules.
"""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele, ...'

from rules_util.api import make_api
import rules_util.error as error
import constants

# Note: Prefix any internal function with an underscore ('_') so that they are
# not imported globally as a callable rule.

# Two required arguments.
def demo_foo(callback, x, y):
    if y > 10:
        raise error.ApiError('WrongAnswer', 'y is too high ({} > 10)'.format(y))
    return { 'z': x + y }

api_demo_foo = make_api(demo_foo)

# One optional arg.
def demo_bar(callback, x, y=2):
    if y > 10:
        raise error.ApiError('WrongAnswer', 'y is too high ({} > 10)'.format(y))
    return { 'z': x + y }

api_demo_bar, rule_demo_bar = make_api(demo_bar, ['z'])

# Same, but with a complex return type.
def demo_bar2(callback, x, y=2):
    if y > 10:
        raise error.ApiError('WrongAnswer', 'y is too high ({} > 10)'.format(y))
    return { 'z': {'added': x + y, 'subtracted': x - y} }

api_demo_bar2, rule_demo_bar2 = make_api(demo_bar2, ['z'])

# Only kwargs (anything goes).
def demo_baz(callback, **bla):
    return { 'z': bla['ans'] if 'ans' in bla else 42 }

api_demo_baz, rule_demo_baz = make_api(demo_baz, ['z'])

# Only optional args.
def demo_foobar(callback, x=40, y=2):
    if y > 10:
        raise error.ApiError('WrongAnswer', 'y is too high ({} > 10)'.format(y))
    return { 'z': x + y }

api_demo_foobar, rule_demo_foobar = make_api(demo_foobar, ['z'])
