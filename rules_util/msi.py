# -*- coding: utf-8 -*-
"""iRODS microservice wrappers that provide primitive error handling

Microservices may fail and indicate failure in a number of different ways.
With this module, we aim to unify microservice error handling by converting
all errors to unambiguous Python exceptions.
"""

__copyright__ = 'Copyright (c) 2019, Utrecht University'
__author__    = 'Chris Smeele, ...'

import error

# Machinery for wrapping microservices and creating microservice-specific exceptions. {{{

def make_msi_exception(name, message):
    """Create a UUMsiException subtype for a specific microservice"""

    t = type('{}Exception'.format(name), (error.UUMsiException,), {})
    t.__init__ = lambda self, status, code, args, e = None: \
        super(t, self).__init__(message, status, code, args, e)
    return t


def run_msi(msi, exception, *args):
    """Run an MSI such that it throws an MSI-specific exception on failure."""
    try:
        ret = msi(*args)
    except RuntimeError as e:
        # msi failures may be raised as non-specific RuntimeErrors.
        # There is no result to save, but we can still convert this to a
        # msi-specific exception.
        raise exception(None, None, None, e)

    if not ret['status']:
        # False status indicates error.
        raise exception(ret['status'],
                        ret['code'],
                        ret['arguments'])
    return ret


def wrap_msi(msi, exception):
    """Wrap an MSI such that it throws an MSI-specific exception on failure.
       The arguments to the wrapper are the same as that of the msi, only with
       a callback in front.

       e.g.:    callback.msiDataObjCreate(x, y, z)
       becomes: data_obj_create(callback, x, y, z)
    """
    return lambda callback, *args: run_msi(getattr(callback, msi), exception, *args)


def make_msi(name, error_text):
    """Creates msi wrapper function and exception type as a tuple.
       (see functions above)
    """
    e = make_msi_exception(name, error_text)
    return (wrap_msi('msi' + name, e), e)


# }}}
# Microservice wrappers {{{

# This naming scheme follows the original msi name, changed to snake_case.
# Note: there is no 'msi_' prefix:
# When imported without '*', these msis are callable as msi.coll_create(), etc.

data_obj_create, DataObjCreateException = make_msi('DataObjCreate', 'Could not create data object')
data_obj_open,   DataObjOpenException   = make_msi('DataObjOpen',   'Could not open data object')
data_obj_read,   DataObjReadException   = make_msi('DataObjRead',   'Could not read data object')
data_obj_write,  DataObjWriteException  = make_msi('DataObjWrite',  'Could not write data object')
data_obj_close,  DataObjCloseException  = make_msi('DataObjClose',  'Could not close data object')
data_obj_copy,   DataObjCopyException   = make_msi('DataObjCopy',   'Could not copy data object')
data_obj_unlink, DataObjUnlinkException = make_msi('DataObjUnlink', 'Could not remove data object')
coll_create,     CollCreateException    = make_msi('CollCreate',    'Could not create collection')
rm_coll,         RmCollException        = make_msi('RmColl',        'Could not remove collection')
check_access,    CheckAccessException   = make_msi('CheckAccess',   'Could not check access')
set_acl,         SetACLException        = make_msi('SetACL',        'Could not set ACL')
get_icat_time,   GetIcatTimeException   = make_msi('GetIcatTime',   'Could not get Icat time')

string_2_key_val_pair, String2KeyValPairException = \
    make_msi('String2KeyValPair', 'Could not create keyval pair')

set_key_value_pairs_to_obj, SetKeyValuePairsToObjException = \
    make_msi('SetKeyValuePairsToObj', 'Could not set metadata on object')

associate_key_value_pairs_to_obj, AssociateKeyValuePairsToObjException = \
    make_msi('AssociateKeyValuePairsToObj', 'Could not associate metadata to object')

# Add new msis here as needed.

# }}}
