import py
import py.__.code.safe_repr

class Frame(object):
    """Wrapper around a Python frame holding f_locals and f_globals
    in which expressions can be evaluated."""

    def __init__(self, frame):
        self.code = py.code.Code(frame.f_code)
        self.lineno = frame.f_lineno - 1
        self.f_globals = frame.f_globals
        self.f_locals = frame.f_locals
        self.raw = frame

    def statement(self):
        return self.code.fullsource.getstatement(self.lineno)
    statement = property(statement, None, None,
                         "statement this frame is at")

    def eval(self, code, **vars):
        f_locals = self.f_locals.copy() 
        f_locals.update(vars)
        return eval(code, self.f_globals, f_locals)

    def exec_(self, code, **vars):
        f_locals = self.f_locals.copy() 
        f_locals.update(vars)
        exec code in self.f_globals, f_locals 

    def repr(self, object):
        return py.__.code.safe_repr._repr(object)

    def is_true(self, object):
        return object

    def getargs(self):
        retval = []
        for arg in self.code.getargs():
            retval.append((arg, self.f_locals[arg]))
        return retval
