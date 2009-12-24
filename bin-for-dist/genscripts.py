import py

bindir = py.path.local(__file__).dirpath().dirpath("bin")
assert bindir.check(), bindir

def getbasename(name):
    assert name[:2] == "py"
    return "py." + name[2:]

def genscript_unix(name):
    basename = getbasename(name)
    path = bindir.join(basename)
    path.write(py.code.Source("""
        #!/usr/bin/env python
        from _findpy import py
        py.cmdline.%s()
    """ % name).strip())
    path.chmod(0755)

def genscript_windows(name):
    basename = getbasename(name)
    winbasename = basename + ".cmd"
    path = bindir.join("win32").join(winbasename)
    path.write(py.code.Source("""
         @echo off
         python "%%~dp0\..\%s" %%*
    """ % (basename)).strip())

if __name__ == "__main__":
    for name in dir(py.cmdline):
        if name[0] != "_":
            genscript_unix(name)
            genscript_windows(name)
