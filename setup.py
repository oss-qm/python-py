"""
autogenerated by gensetup.py
setup file for 'py' package based on:
        
tags: tip
branch: 1.0.x
revision: 1173:33348724fd55e40d1dfaab26575811a1ecdd38f1
         
"""
import os, sys
        
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
            
long_description = """

advanced testing and development support library: 

- `py.test`_: cross-project testing tool with many advanced features
- `py.execnet`_: ad-hoc code distribution to SSH, Socket and local sub processes
- `py.path`_: path abstractions over local and subversion files 
- `py.code`_: dynamic code compile and traceback printing support

Compatibility: Linux, Win32, OSX, Python versions 2.3-2.6. 
For questions please check out http://pylib.org/contact.html

.. _`py.test`: http://pylib.org/test.html
.. _`py.execnet`: http://pylib.org/execnet.html
.. _`py.path`: http://pylib.org/path.html
.. _`py.code`: http://pylib.org/code.html


"""
def main():
    setup(
        name='py',
        description='py.test and pylib: advanced testing tool and networking lib',
        long_description = long_description, 
        version='1.0.x', 
        url='http://pylib.org', 
        license='MIT license',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'], 
        author='holger krekel, Guido Wesdorp, Carl Friedrich Bolz, Armin Rigo, Maciej Fijalkowski & others',
        author_email='holger at merlinux.eu, py-dev at codespeak.net',
        
        entry_points={'console_scripts': ['py.cleanup = py.cmdline:pycleanup',
                                          'py.countloc = py.cmdline:pycountloc',
                                          'py.lookup = py.cmdline:pylookup',
                                          'py.rest = py.cmdline:pyrest',
                                          'py.svnwcrevert = py.cmdline:pysvnwcrevert',
                                          'py.test = py.cmdline:pytest',
                                          'py.which = py.cmdline:pywhich']},
        classifiers=['Development Status :: 5 - Stable',
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
        packages=['py.builtin',
                  'py.builtin.testing',
                  'py.cmdline',
                  'py.cmdline.testing',
                  'py.code',
                  'py.code.testing',
                  'py.compat',
                  'py.compat.testing',
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
                             'compat/LICENSE',
                             'compat/testing/test_doctest.txt',
                             'compat/testing/test_doctest2.txt',
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
        