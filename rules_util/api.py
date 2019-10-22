# -*- coding: utf-8 -*-
"""Functions for creating API rules.

For example usage, see make_api() or rules_demo/test1.py
"""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele'

from rule import *
import json
import json_utils
import error
import inspect
import traceback
from collections import OrderedDict


def api(f):
    """Turn a Python function into a basic API function.

    By itself, this wrapper is not very useful, as the resulting function is
    not callable by rules. See make_api() below for a method to turn the
    result into one or two rules, with different calling conventions.

    api() creates a function that takes a JSON string as an argument,
    and translates it to function arguments for `f`. The JSON input is
    automatically validated for required/optional arguments, based on f()'s
    signature.

    f()'s returned value should always be a dict. If errors occur,
    the 'error' and 'error_message' fields are populated.
    """
    # Determine required and optional argument names from the function signature.
    a_pos, a_var, a_kw, a_defaults = inspect.getargspec(f)
    a_pos = a_pos[1:] # ignore callback param.

    required = set(a_pos if a_defaults is None else a_pos[:-len(a_defaults) ])
    optional = set([]    if a_defaults is None else a_pos[ -len(a_defaults):])

    # If the function accepts **kwargs, we do not forbid extra arguments.
    allow_extra = a_kw is not None

    # XXX Debug {{{
    # print('api-ify   {}'.format(f.__name__))
    # print('spec:     {}'.format(inspect.getargspec(f)))
    # print('required: {}'.format(required))
    # print('optional: {}{}'.format(optional, ' + kwargs' if allow_extra else ''))
    # print('defaults: {}'.format(a_defaults))
    # }}}

    def wrapper(callback, inp):
        """A function that receives a JSON string and calls a wrapped function with unpacked arguments."""
        # Validate input string: is it a valid JSON object?
        try:
            data = json_utils.parse_json(inp)
            if type(data) is not OrderedDict:
                raise error.JsonException('Argument is not a JSON object')
        except error.JsonException:
            callback.writeString('serverLog', 'Error: API rule <{}> called with invalid JSON argument'
                                              .format(f.__name__))
            return {'error': 'BadRequest', 'error_message': 'Internal error'}

        # Check that required arguments are present.
        for param in required:
            if param not in data:
                callback.writeString('serverLog', 'Error: API rule <{}> called with missing <{}> argument'
                                                  .format(f.__name__, param))
                return {'error': 'BadRequest', 'error_message': 'Internal error'}

        # Forbid arguments that are not in the function signature.
        if not allow_extra:
            for param in data:
                if param not in required | optional:
                    callback.writeString('serverLog', 'Error: API rule <{}> called with unrecognized <{}> argument'
                                                      .format(f.__name__, param))
                    return {'error': 'BadRequest', 'error_message': 'Internal error'}

        # Try to run the function with the supplied arguments,
        # catching any error it throws.
        try:
            result = f(callback, **data)
            if type(result) is error.ApiError:
                raise result # Allow ApiErrors to be either raised or returned.
            return result
        except error.ApiError as e:
            # A proper caught error with name and message.
            callback.writeString('serverLog', 'Error: API rule <{}> failed with error <{}>'.format(f.__name__, e))
            return e.as_dict()
        except Exception as e:
            # An uncaught error. Log a trace to aid debugging.
            callback.writeString('serverLog', 'Error: API rule <{}> failed with uncaught error (trace follows below this line)\n{}'
                                              .format(f.__name__, traceback.format_exc()))
            return {'error': 'Internal', 'error_message': 'Internal error'}

    return wrapper


def make_api(f, rule_output_names=[]):
    """Create API functions callable as iRODS rules.

    This translate between a Python calling convention and the iRODS rule
    calling convention.

    Two types of API rules can be created this way:

    - If no rule_output_names are given:
      An iRODS rule is created that receives a JSON string and prints the
      result of f, JSON-encoded to stdout. If an error occurs, the output JSON
      will contain "error" and "error_message" items.

    - If rule_output_names are given:
      Two rules are created: One the same as the above, however the other
      stores its outputs in the rule output parameters with the given names.
      Also, the *error and *error_message output parameters are implicitly
      added to this rule, and will contain an ApiError if raised.

    For example:

        def demo_foo(callback, x, y=2):
            if y > 10:
                raise error.ApiError('WrongAnswer', 'y is too high ({} > 10)'.format(y))
            return { 'result': x + y }

        api_demo_foo, rule_demo_foo = make_api(demo_foo, ['result'])

    Produces two rules. They can be called as follows (from the iRODS rule language, PRODS or irule):

        api_demo_foo('{"x": 40}');  # prints '{"result": 42}' on stdout.

        *result = '';
        rule_demo_foo('{"x": 40}', *result, *error, *error_message); # *result becomes "42"

    (of course, the original Python function itself is also still callable from
    other Python rules)
    """

    # The "base" API function, that does handling of arguments and errors.
    base = api(f)

    # The JSON-in, JSON-out rule.
    json_json_api = rule_cc(inputs=[0], outputs=[], transform=json.dumps, handler=RuleOutput.STDOUT)(base)

    # Should we create a rule that uses output parameters as well?
    if len(rule_output_names) == 0:
        # No.
        return json_json_api

    # These rule output parameters must always be present.
    rule_output_names += ['error', 'error_message']

    # The JSON-in, strings-args-out rule.
    @rule_cc(inputs=[0], outputs=range(1,1+len(rule_output_names)))
    def json_rule_api(callback, inp):
        result = base(callback, inp)
        # Missing outputs result in empty strings.
        return tuple([result.get(name, '') for name in rule_output_names])

    return json_json_api, json_rule_api
