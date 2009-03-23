"""
    setup file for 'py' package based on:

        https://codespeak.net/svn/py/trunk, revision=63240

    autogenerated by gensetup.py
"""
import os, sys
        
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension
        
long_description = """

The py lib is an extensible library for testing, distributed processing and 
interacting with filesystems. 

- `py.test`_: cross-project testing tool with many advanced features
- `py.execnet`_: ad-hoc code distribution to SSH, Socket and local sub processes
- `py.magic.greenlet`_: micro-threads on standard CPython ("stackless-light") and PyPy
- `py.path`_: path abstractions over local and subversion files 
- `py.code`_: dynamic code compile and traceback printing support

The py lib and its tools should work well on Linux, Win32, 
OSX, Python versions 2.3-2.6.  For questions please go to
http://pylib.org/contact.html

.. _`py.test`: http://pylib.org/test.html
.. _`py.execnet`: http://pylib.org/execnet.html
.. _`py.magic.greenlet`: http://pylib.org/greenlet.html
.. _`py.path`: http://pylib.org/path.html
.. _`py.code`: http://pylib.org/code.html


"""
def main():
    setup(
        name='py',
        description='pylib and py.test: agile development and test support library',
        long_description = long_description, 
        version='1.0.0a6', 
        url='http://pylib.org', 
        download_url='http://codespeak.net/py/1.0.0a6/download.html', 
        license='MIT license',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'], 
        author='holger krekel, Guido Wesdorp, Carl Friedrich Bolz, Armin Rigo, Maciej Fijalkowski & others',
        author_email='holger at merlinux.eu, py-dev at codespeak.net',
        ext_modules = [Extension("py.c-extension.greenlet.greenlet", 
            ["py/c-extension/greenlet/greenlet.c"]),],
        
        entry_points={'console_scripts': ['py.cleanup = py.cmdline:pycleanup',
                                          'py.countloc = py.cmdline:pycountloc',
                                          'py.lookup = py.cmdline:pylookup',
                                          'py.rest = py.cmdline:pyrest',
                                          'py.svnwcrevert = py.cmdline:pysvnwcrevert',
                                          'py.test = py.cmdline:pytest',
                                          'py.which = py.cmdline:pywhich']},
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Testing',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: System :: Distributed Computing',
                     'Topic :: Utilities',
                     'Programming Language :: Python'],
        packages=['py',
                  'py.builtin',
                  'py.builtin.testing',
                  'py.c-extension',
                  'py.cmdline',
                  'py.cmdline.testing',
                  'py.code',
                  'py.code.testing',
                  'py.compat',
                  'py.compat.testing',
                  'py.doc',
                  'py.execnet',
                  'py.execnet.script',
                  'py.execnet.testing',
                  'py.io',
                  'py.io.testing',
                  'py.log',
                  'py.log.testing',
                  'py.magic',
                  'py.magic.testing',
                  'py.misc',
                  'py.misc.cmdline',
                  'py.misc.testing',
                  'py.path',
                  'py.path.gateway',
                  'py.path.local',
                  'py.path.local.testing',
                  'py.path.svn',
                  'py.path.svn.testing',
                  'py.path.testing',
                  'py.process',
                  'py.process.testing',
                  'py.rest',
                  'py.rest.testing',
                  'py.test',
                  'py.test.dist',
                  'py.test.dist.testing',
                  'py.test.looponfail',
                  'py.test.looponfail.testing',
                  'py.test.plugin',
                  'py.test.testing',
                  'py.test.testing.import_test.package',
                  'py.test.web',
                  'py.thread',
                  'py.thread.testing',
                  'py.tool',
                  'py.tool.testing',
                  'py.xmlobj',
                  'py.xmlobj.testing'],
        package_data={'py': ['LICENSE',
                             'bin/_findpy.py',
                             'bin/_genscripts.py',
                             'bin/gendoc.py',
                             'bin/py.cleanup',
                             'bin/py.countloc',
                             'bin/py.lookup',
                             'bin/py.rest',
                             'bin/py.svnwcrevert',
                             'bin/py.test',
                             'bin/py.which',
                             'bin/win32/py.cleanup.cmd',
                             'bin/win32/py.countloc.cmd',
                             'bin/win32/py.lookup.cmd',
                             'bin/win32/py.rest.cmd',
                             'bin/win32/py.svnwcrevert.cmd',
                             'bin/win32/py.test.cmd',
                             'bin/win32/py.which.cmd',
                             'c-extension/greenlet/README.txt',
                             'c-extension/greenlet/dummy_greenlet.py',
                             'c-extension/greenlet/greenlet.c',
                             'c-extension/greenlet/greenlet.h',
                             'c-extension/greenlet/setup.py',
                             'c-extension/greenlet/slp_platformselect.h',
                             'c-extension/greenlet/switch_amd64_unix.h',
                             'c-extension/greenlet/switch_mips_unix.h',
                             'c-extension/greenlet/switch_ppc_macosx.h',
                             'c-extension/greenlet/switch_ppc_unix.h',
                             'c-extension/greenlet/switch_s390_unix.h',
                             'c-extension/greenlet/switch_sparc_sun_gcc.h',
                             'c-extension/greenlet/switch_x86_msvc.h',
                             'c-extension/greenlet/switch_x86_unix.h',
                             'c-extension/greenlet/test_generator.py',
                             'c-extension/greenlet/test_generator_nested.py',
                             'c-extension/greenlet/test_greenlet.py',
                             'c-extension/greenlet/test_remote.py',
                             'c-extension/greenlet/test_throw.py',
                             'compat/LICENSE',
                             'compat/testing/test_doctest.txt',
                             'compat/testing/test_doctest2.txt',
                             'doc/bin.txt',
                             'doc/code.txt',
                             'doc/coding-style.txt',
                             'doc/contact.txt',
                             'doc/download.txt',
                             'doc/draft_pyfs',
                             'doc/execnet.txt',
                             'doc/future.txt',
                             'doc/greenlet.txt',
                             'doc/impl-test.txt',
                             'doc/index.txt',
                             'doc/io.txt',
                             'doc/links.txt',
                             'doc/log.txt',
                             'doc/misc.txt',
                             'doc/path.txt',
                             'doc/release-0.9.0.txt',
                             'doc/release-0.9.2.txt',
                             'doc/style.css',
                             'doc/test-config.txt',
                             'doc/test-dist.txt',
                             'doc/test-examples.txt',
                             'doc/test-ext.txt',
                             'doc/test-features.txt',
                             'doc/test-plugins.txt',
                             'doc/test-quickstart.txt',
                             'doc/test.txt',
                             'doc/why_py.txt',
                             'doc/xml.txt',
                             'env.cmd',
                             'execnet/NOTES',
                             'execnet/improve-remote-tracebacks.txt',
                             'misc/testing/data/svnlookrepo.dump',
                             'path/gateway/TODO.txt',
                             'path/svn/quoting.txt',
                             'path/svn/testing/repotest.dump',
                             'rest/rest.sty.template',
                             'rest/testing/data/example.rst2pdfconfig',
                             'rest/testing/data/example1.dot',
                             'rest/testing/data/formula.txt',
                             'rest/testing/data/formula1.txt',
                             'rest/testing/data/graphviz.txt',
                             'rest/testing/data/part1.txt',
                             'rest/testing/data/part2.txt',
                             'rest/testing/data/tocdepth.rst2pdfconfig']},
        zip_safe=False,
    )

if __name__ == '__main__':
    main()
        