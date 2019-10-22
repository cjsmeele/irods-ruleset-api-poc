# -*- coding: utf-8 -*-
"""Python rule tracing (debug feature)."""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele'

def trace_on(globs):
    """Wrap all toplevel Python functions to print timing information.

    This also visualizes the execution path by indenting trace lines with
    the current stack depth.

    Each line shows a timestamp at execution time, the execution length, and
    the function name. Lines are printed after execution compeletes, so
    nested function calls appear *above* parent functions.

    To enable tracing, include the following at the end of core.py:

        import rules_util.trace as trace
        trace.trace_on(globals())
    """
    import inspect
    import time
    from types import FunctionType

    def wrap(fn, name):
        def wrapper(*args, **kwargs):
            depth = len(inspect.stack()) // 2
            x = time.time()
            result = fn(*args, **kwargs)
            y = time.time()
            print('TRACE: [%010.3f]+%4dms %s %s' % (x, int((y-x)*1000), '*'*depth, name))
            return result
        return wrapper
    g = list(filter(lambda (_,x): type(x) is FunctionType, globs.items()))
    for name, fn in g:
        globs[name] = wrap(fn, name)
