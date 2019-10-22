# -*- coding: utf-8 -*-
"""Experimental Python/Rule interface code."""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele'

from error import *
from enum  import Enum
import json

class RuleOutput(Enum):
    """Specifies rule output handlers."""
    STORE      = 0 # store in output parameters
    STDOUT     = 1 # write to stdout
    STDOUT_BIN = 2 # write to stdout, without a trailing newline

def rule_cc(inputs=None, outputs=None, transform=lambda x: x, handler=RuleOutput.STORE):
    """Creates a rule (with iRODS calling conventions) from a Python function.

    Decorator arguments:

    inputs and outputs can optionally be specified as lists of indices to
    influence how parameters are passed to this function, and how the return
    value is processed. By default, 'inputs' and 'outputs' both span all rule arguments.

    transform can be used to apply a transformation to the returned value(s),
    e.g. by encoding them as JSON.

    handler specifies what to do with the (transformed) return value(s):
    - RuleOutput.STORE:      stores return value(s) in output parameter(s) (this is the default)
    - RuleOutput.STDOUT:     prints return value(s) to stdout
    - RuleOutput.STDOUT_BIN: prints return value(s) to stdout, without a trailing newline

    Examples:

        @rule_cc(inputs=[0,1], outputs=[2])
        def foo(callback, x, y):
            return int(x) + int(y)

    is equivalent to:

        def foo(rule_args, callback, rei):
            x, y = rule_args[0:2]
            rule_args[2] = int(x) + int(y)

    and...

        @rule_cc(transform=json.dumps, handler=RuleOutput.STDOUT)
        def foo(callback, x, y):
            return {'result': int(x) + int(y)}

    is equivalent to:

        def foo(rule_args, callback, rei):
            x, y = rule_args[0:2]
            callback.writeString('stdout', json.dumps(int(x) + int(y)))
    """
    def encode_val(v):
        """Encode a value such that it can be safely transported in rule_args, as output."""
        if type(v) is str:
            return v
        else:
            # Encode numbers, bools, lists and dictionaries as JSON strings.
            # note: the result of encoding e.g. int(5) should be equal to str(int(5)).
            return json.dumps(v)

    def deco(f):
        def r(rule_args, callback, rei):
            result = f(callback, *rule_args if inputs is None else [rule_args[i] for i in inputs])

            if result is None:
                return

            result = map(transform, list(result) if type(result) is tuple else [result])

            if handler is RuleOutput.STORE:
                if outputs is None:
                    # outputs not specified? overwrite all arguments.
                    rule_args[:] = map(encode_val, result)
                else:
                    # set specific output arguments.
                    for i, x in zip(outputs, result):
                        rule_args[i] = encode_val(x)
            elif handler is RuleOutput.STDOUT:
                for x in result:
                    callback.writeString('stdout', encode_val(x)+'\n')
                    # XXX for debugging:
                    # callback.writeString('serverLog', 'rule output (DEBUG): ' + encode_val(x))
            elif handler is RuleOutput.STDOUT_BIN:
                for x in result:
                    callback.writeString('stdout', encode_val(x))
        return r
    return deco
