import os, sys
from py.path import local

def autopath(globs=None):
    """ return the (local) path of the "current" file pointed to by globals
        or - if it is none - alternatively the callers frame globals.

        the path will always point to a .py file  or to None.
        the path will have the following payload:
        pkgdir   is the last parent directory path containing __init__.py 
    """
    if globs is None:
        globs = sys._getframe(1).f_globals
    try:
        __file__ = globs['__file__']
    except KeyError:
        if not sys.argv[0]:
            raise ValueError, "cannot compute autopath in interactive mode"
        __file__ = os.path.abspath(sys.argv[0])

    ret = local(__file__)
    if ret.ext in ('.pyc', '.pyo'):
        ret = ret.new(ext='.py')
    current = pkgdir = ret.dirpath()
    while 1:
        if current.join('__init__.py').check():
            pkgdir = current
            current = current.dirpath()
            if pkgdir != current:
                continue
        elif str(current) not in sys.path:
            sys.path.insert(0, str(current))
        break
    ret.pkgdir = pkgdir
    return ret
