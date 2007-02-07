import py
import os
import inspect
from py.__.apigen.layout import LayoutPage
from py.__.apigen.source import browser as source_browser
from py.__.apigen.source import html as source_html
from py.__.apigen.source import color as source_color
from py.__.apigen.tracer.description import is_private
from py.__.apigen.rest.genrest import split_of_last_part
from py.__.apigen.linker import relpath
from py.__.apigen.html import H

sorted = py.builtin.sorted
html = py.xml.html
raw = py.xml.raw

def is_navigateable(name):
    return (not is_private(name) and name != '__doc__')

def show_property(name):
    if not name.startswith('_'):
        return True
    if name.startswith('__') and name.endswith('__'):
        # XXX do we need to skip more manually here?
        if (name not in dir(object) and
                name not in ['__doc__', '__dict__', '__name__', '__module__',
                             '__weakref__']):
            return True
    return False

def deindent(str, linesep='\n'):
    """ de-indent string

        can be used to de-indent Python docstrings, it de-indents the first
        line to the side always, and determines the indentation of the rest
        of the text by taking that of the least indented (filled) line
    """
    lines = str.strip().split(linesep)
    normalized = []
    deindent = None
    normalized.append(lines[0].strip())
    # replace tabs with spaces, empty lines that contain spaces only, and
    # find out what the smallest indentation is
    for line in lines[1:]:
        line = line.replace('\t', ' ' * 4)
        stripped = line.strip()
        if not stripped:
            normalized.append('')
        else:
            rstripped = line.rstrip()
            indent = len(rstripped) - len(stripped)
            if deindent is None or indent < deindent:
                deindent = indent
            normalized.append(line)
    ret = [normalized[0]]
    for line in normalized[1:]:
        if not line:
            ret.append(line)
        else:
            ret.append(line[deindent:])
    return '%s\n' % (linesep.join(ret),)

def get_linesep(s, default='\n'):
    """ return the line seperator of a string

        returns 'default' if no seperator can be found
    """
    for sep in ('\r\n', '\r', '\n'):
        if sep in s:
            return sep
    return default

def get_param_htmldesc(linker, func):
    """ get the html for the parameters of a function """
    import inspect
    # XXX copy and modify formatargspec to produce html
    return inspect.formatargspec(*inspect.getargspec(func))

# some helper functionality
def source_dirs_files(fspath):
    """ returns a tuple (dirs, files) for fspath

        dirs are all the subdirs, files are the files which are interesting
        in building source documentation for a Python code tree (basically all
        normal files excluding .pyc and .pyo ones)

        all files and dirs that have a name starting with . are considered
        hidden
    """
    dirs = []
    files = []
    for child in fspath.listdir():
        if child.basename.startswith('.'):
            continue
        if child.check(dir=True):
            dirs.append(child)
        elif child.check(file=True):
            if child.ext in ['.pyc', '.pyo']:
                continue
            files.append(child)
    return sorted(dirs), sorted(files)

def create_namespace_tree(dotted_names):
    """ creates a tree (in dict form) from a set of dotted names
    """
    ret = {}
    for dn in dotted_names:
        path = dn.split('.')
        for i in xrange(len(path)):
            ns = '.'.join(path[:i])
            itempath = '.'.join(path[:i + 1])
            if ns not in ret:
                ret[ns] = []
            if itempath not in ret[ns]:
                ret[ns].append(itempath)
    return ret

def wrap_page(project, title, contentel, navel, relbase, basepath,
              pageclass):
    page = pageclass(project, title, nav=navel, encoding='UTF-8',
                      relpath=relbase)
    page.set_content(contentel)
    page.setup_scripts_styles(basepath)
    return page

def enumerate_and_color(codelines, firstlineno, enc):
    snippet = H.SourceCode()
    tokenizer = source_color.Tokenizer(source_color.PythonSchema)
    for i, line in enumerate(codelines):
        try:
            snippet.add_line(i + firstlineno + 1,
                             source_html.prepare_line([line], tokenizer, enc))
        except py.error.ENOENT:
            # error reading source code, giving up
            snippet = org
            break
    return snippet

def get_obj(pkg, dotted_name):
    full_dotted_name = '%s.%s' % (pkg.__name__, dotted_name)
    if dotted_name == '':
        return pkg
    path = dotted_name.split('.')
    ret = pkg
    for item in path:
        marker = []
        ret = getattr(ret, item, marker)
        if ret is marker:
            raise NameError('can not access %s in %s' % (item,
                                                         full_dotted_name))
    return ret

# the PageBuilder classes take care of producing the docs (using the stuff
# above)
class AbstractPageBuilder(object):
    pageclass = LayoutPage
    
    def write_page(self, title, reltargetpath, tag, nav):
        targetpath = self.base.join(reltargetpath)
        relbase= relpath('%s%s' % (targetpath.dirpath(), targetpath.sep),
                         self.base.strpath + '/')
        page = wrap_page(self.project, title, tag, nav, relbase, self.base,
                         self.pageclass)
        # we write the page with _temporary_ hrefs here, need to be replaced
        # from the TempLinker later
        content = page.unicode()
        targetpath.ensure()
        targetpath.write(content.encode("utf8"))

class SourcePageBuilder(AbstractPageBuilder):
    """ builds the html for a source docs page """
    def __init__(self, base, linker, projroot, project, capture=None,
                 pageclass=LayoutPage):
        self.base = base
        self.linker = linker
        self.projroot = projroot
        self.project = project
        self.capture = capture
        self.pageclass = pageclass
    
    def build_navigation(self, fspath):
        nav = H.Navigation(class_='sidebar')
        relpath = fspath.relto(self.projroot)
        path = relpath.split(os.path.sep)
        indent = 0
        # build links to parents
        if relpath != '':
            for i in xrange(len(path)):
                dirpath = os.path.sep.join(path[:i])
                abspath = self.projroot.join(dirpath).strpath
                if i == 0:
                    text = self.projroot.basename
                else:
                    text = path[i-1]
                nav.append(H.NavigationItem(self.linker, abspath, text,
                                            indent, False))
                indent += 1
        # build siblings or children and self
        if fspath.check(dir=True):
            # we're a dir, build ourselves and our children
            dirpath = fspath
            nav.append(H.NavigationItem(self.linker, dirpath.strpath,
                                        dirpath.basename, indent, True))
            indent += 1
        elif fspath.strpath == self.projroot.strpath:
            dirpath = fspath
        else:
            # we're a file, build our parent's children only
            dirpath = fspath.dirpath()
        diritems, fileitems = source_dirs_files(dirpath)
        for dir in diritems:
            nav.append(H.NavigationItem(self.linker, dir.strpath, dir.basename,
                                        indent, False))
        for file in fileitems:
            selected = (fspath.check(file=True) and
                        file.basename == fspath.basename)
            nav.append(H.NavigationItem(self.linker, file.strpath,
                                        file.basename, indent, selected))
        return nav

    re = py.std.re
    _reg_body = re.compile(r'<body[^>]*>(.*)</body>', re.S)
    def build_python_page(self, fspath):
        # XXX two reads of the same file here... not very bad (disk caches
        # and such) but also not very nice...
        enc = source_html.get_module_encoding(fspath.strpath)
        source = fspath.read()
        sep = get_linesep(source)
        colored = enumerate_and_color(source.split(sep), 0, enc)
        tag = H.SourceDef(colored)
        nav = self.build_navigation(fspath)
        return tag, nav

    def build_dir_page(self, fspath):
        dirs, files = source_dirs_files(fspath)
        dirs = [(p.basename, self.linker.get_lazyhref(str(p))) for p in dirs]
        files = [(p.basename, self.linker.get_lazyhref(str(p))) for p in files]
        tag = H.DirList(dirs, files)
        nav = self.build_navigation(fspath)
        return tag, nav

    def build_nonpython_page(self, fspath):
        try:
            tag = H.NonPythonSource(unicode(fspath.read(), 'utf-8'))
        except UnicodeError:
            tag = H.NonPythonSource('no source available (binary file?)')
        nav = self.build_navigation(fspath)
        return tag, nav

    def build_pages(self, base):
        for fspath in [base] + list(base.visit()):
            if fspath.ext in ['.pyc', '.pyo']:
                continue
            if self.capture:
                self.capture.err.writeorg('.')
            relfspath = fspath.relto(base)
            if relfspath.find('%s.' % (os.path.sep,)) > -1:
                # skip hidden dirs and files
                continue
            elif fspath.check(dir=True):
                if relfspath != '':
                    relfspath += os.path.sep
                reloutputpath = 'source%s%sindex.html' % (os.path.sep,
                                                          relfspath)
            else:
                reloutputpath = "source%s%s.html" % (os.path.sep, relfspath)
            reloutputpath = reloutputpath.replace(os.path.sep, '/')
            outputpath = self.base.join(reloutputpath)
            self.linker.set_link(str(fspath), reloutputpath)
            self.build_page(fspath, outputpath, base)

    def build_page(self, fspath, outputpath, base):
        """ build syntax-colored source views """
        if fspath.check(ext='.py'):
            try:
                tag, nav = self.build_python_page(fspath)
            except (KeyboardInterrupt, SystemError):
                raise
            except: # XXX strange stuff going wrong at times... need to fix
                raise
                exc, e, tb = py.std.sys.exc_info()
                print '%s - %s' % (exc, e)
                print
                print ''.join(py.std.traceback.format_tb(tb))
                print '-' * 79
                del tb
                tag, nav = self.build_nonpython_page(fspath)
        elif fspath.check(dir=True):
            tag, nav = self.build_dir_page(fspath)
        else:
            tag, nav = self.build_nonpython_page(fspath)
        title = 'sources for %s' % (fspath.basename,)
        reltargetpath = outputpath.relto(self.base).replace(os.path.sep,
                                                            '/')
        self.write_page(title, reltargetpath, tag, nav)

class ApiPageBuilder(AbstractPageBuilder):
    """ builds the html for an api docs page """
    def __init__(self, base, linker, dsa, projroot, namespace_tree, project,
                 capture=None, pageclass=LayoutPage):
        self.base = base
        self.linker = linker
        self.dsa = dsa
        self.projroot = projroot
        self.projpath = py.path.local(projroot)
        self.namespace_tree = namespace_tree
        self.project = project
        self.capture = capture
        self.pageclass = pageclass

        pkgname = self.dsa.get_module_name().split('/')[-1]
        self.pkg = __import__(pkgname)

    def build_callable_view(self, dotted_name):
        """ build the html for a class method """
        # XXX we may want to have seperate
        func = get_obj(self.pkg, dotted_name)
        docstring = func.__doc__ 
        if docstring:
            docstring = deindent(docstring)
        localname = func.__name__
        argdesc = get_param_htmldesc(self.linker, func)
        valuedesc = self.build_callable_signature_description(dotted_name)

        sourcefile = inspect.getsourcefile(func)
        callable_source = self.dsa.get_function_source(dotted_name)
        # i assume they're both either available or unavailable(XXX ?)
        is_in_pkg = self.is_in_pkg(sourcefile)
        href = None
        text = 'could not get to source file'
        colored = []
        if sourcefile and callable_source:
            enc = source_html.get_module_encoding(sourcefile)
            tokenizer = source_color.Tokenizer(source_color.PythonSchema)
            firstlineno = func.func_code.co_firstlineno
            sep = get_linesep(callable_source)
            org = callable_source.split(sep)
            colored = [enumerate_and_color(org, firstlineno, enc)]
            text = 'source: %s' % (sourcefile,)
            if is_in_pkg:
                href = self.linker.get_lazyhref(sourcefile)

        csource = H.SourceSnippet(text, href, colored)
        callstack = self.dsa.get_function_callpoints(dotted_name)
        csitems = []
        for cs, _ in callstack:
            csitems.append(self.build_callsite(dotted_name, cs))
        snippet = H.FunctionDescription(localname, argdesc, docstring,
                                        valuedesc, csource, csitems)
        
        return snippet

    def build_class_view(self, dotted_name):
        """ build the html for a class """
        cls = get_obj(self.pkg, dotted_name)
        # XXX is this a safe check?
        try:
            sourcefile = inspect.getsourcefile(cls)
        except TypeError:
            sourcefile = None

        docstring = cls.__doc__
        if docstring:
            docstring = deindent(docstring)
        if not hasattr(cls, '__name__'):
            clsname = 'instance of %s' % (cls.__class__.__name__,)
        else:
            clsname = cls.__name__
        bases = self.build_bases(dotted_name)
        properties = self.build_properties(cls)
        methods = self.build_methods(dotted_name)

        if sourcefile is None:
            sourcelink = H.div('no source available')
        else:
            if sourcefile[-1] in ['o', 'c']:
                sourcefile = sourcefile[:-1]
            sourcelink = H.div(H.a('view source',
                href=self.linker.get_lazyhref(sourcefile)))

        snippet = H.ClassDescription(
            # XXX bases HTML
            H.ClassDef(clsname, bases, docstring, sourcelink,
                       properties, methods),
        )

        return snippet

    def build_bases(self, dotted_name):
        ret = []
        bases = self.dsa.get_possible_base_classes(dotted_name)
        for base in bases:
            try:
                obj = self.dsa.get_obj(base.name)
            except KeyError:
                ret.append((base.name, None))
            else:
                href = self.linker.get_lazyhref(base.name)
                ret.append((base.name, href))
        return ret

    def build_properties(self, cls):
        properties = []
        for attr in dir(cls):
            val = getattr(cls, attr)
            if show_property(attr) and not callable(val):
                if isinstance(val, property):
                    val = '<property object (dynamically calculated value)>'
                properties.append((attr, val))
        properties.sort(key=lambda a: a[0]) # sort on name
        return properties

    def build_methods(self, dotted_name):
        ret = []
        methods = self.dsa.get_class_methods(dotted_name)
        if '__init__' in methods:
            methods.remove('__init__')
            methods.insert(0, '__init__')
        for method in methods:
            ret += self.build_callable_view('%s.%s' % (dotted_name,
                                                       method))
        return ret

    def build_namespace_view(self, namespace_dotted_name, item_dotted_names):
        """ build the html for a namespace (module) """
        obj = get_obj(self.pkg, namespace_dotted_name)
        docstring = obj.__doc__
        snippet = H.NamespaceDescription(
            H.NamespaceDef(namespace_dotted_name),
            H.Docstring(docstring or '*no docstring available*')
        )
        for dotted_name in sorted(item_dotted_names):
            itemname = dotted_name.split('.')[-1]
            if not is_navigateable(itemname):
                continue
            snippet.append(
                H.NamespaceItem(
                    H.a(itemname,
                        href=self.linker.get_lazyhref(dotted_name)
                    )
                )
            )
        return snippet

    def build_class_pages(self, classes_dotted_names):
        passed = []
        for dotted_name in sorted(classes_dotted_names):
            if self.capture:
                self.capture.err.writeorg('.')
            parent_dotted_name, _ = split_of_last_part(dotted_name)
            try:
                sibling_dotted_names = self.namespace_tree[parent_dotted_name]
            except KeyError:
                # no siblings (built-in module or sth)
                sibling_dotted_names = []
            tag = H.Content(self.build_class_view(dotted_name))
            nav = self.build_navigation(dotted_name, False)
            reltargetpath = "api/%s.html" % (dotted_name,)
            self.linker.set_link(dotted_name, reltargetpath)
            title = 'api documentation for %s' % (dotted_name,)
            self.write_page(title, reltargetpath, tag, nav)
        return passed
        
    def build_function_pages(self, method_dotted_names):
        passed = []
        for dotted_name in sorted(method_dotted_names):
            if self.capture:
                self.capture.err.writeorg('.')
            # XXX should we create a build_function_view instead?
            parent_dotted_name, _ = split_of_last_part(dotted_name)
            sibling_dotted_names = self.namespace_tree[parent_dotted_name]
            tag = H.Content(self.build_callable_view(dotted_name))
            nav = self.build_navigation(dotted_name, False)
            reltargetpath = "api/%s.html" % (dotted_name,)
            self.linker.set_link(dotted_name, reltargetpath)
            title = 'api documentation for %s' % (dotted_name,)
            self.write_page(title, reltargetpath, tag, nav)
        return passed

    def build_namespace_pages(self):
        passed = []
        module_name = self.dsa.get_module_name().split('/')[-1]

        names = self.namespace_tree.keys()
        names.sort()
        function_names = self.dsa.get_function_names()
        class_names = self.dsa.get_class_names()
        for dotted_name in sorted(names):
            if self.capture:
                self.capture.err.writeorg('.')
            if dotted_name in function_names or dotted_name in class_names:
                continue
            subitem_dotted_names = self.namespace_tree[dotted_name]
            tag = H.Content(self.build_namespace_view(dotted_name,
                                                      subitem_dotted_names))
            nav = self.build_navigation(dotted_name, True)
            if dotted_name == '':
                reltargetpath = 'api/index.html'
            else:
                reltargetpath = 'api/%s.html' % (dotted_name,)
            self.linker.set_link(dotted_name, reltargetpath)
            if dotted_name == '':
                dotted_name = self.dsa.get_module_name().split('/')[-1]
            title = 'index of %s namespace' % (dotted_name,)
            self.write_page(title, reltargetpath, tag, nav)
        return passed

    def build_navigation(self, dotted_name, build_children=True):
        navitems = []

        # top namespace, index.html
        module_name = self.dsa.get_module_name().split('/')[-1]
        navitems.append(H.NavigationItem(self.linker, '', module_name, 0,
                                         True))
        def build_nav_level(dotted_name, depth=1):
            navitems = []
            path = dotted_name.split('.')[:depth]
            siblings = self.namespace_tree.get('.'.join(path[:-1]))
            for dn in sorted(siblings):
                selected = dn == '.'.join(path)
                sibpath = dn.split('.')
                sibname = sibpath[-1]
                if not is_navigateable(sibname):
                    continue
                navitems.append(H.NavigationItem(self.linker, dn, sibname,
                                                 depth, selected))
                if selected:
                    lastlevel = dn.count('.') == dotted_name.count('.')
                    if not lastlevel:
                        navitems += build_nav_level(dotted_name, depth+1)
                    elif lastlevel and build_children:
                        # XXX hack
                        navitems += build_nav_level('%s.' % (dotted_name,),
                                                    depth+1)

            return navitems

        navitems += build_nav_level(dotted_name)
        return H.Navigation(class_='sidebar', *navitems)

    def build_callable_signature_description(self, dotted_name):
        args, retval = self.dsa.get_function_signature(dotted_name)
        valuedesc = H.ValueDescList()
        for name, _type in args:
            valuedesc.append(self.build_sig_value_description(name, _type))
        if retval:
            retval = self.process_type_link(retval)
        ret = H.div(H.div('arguments:'), valuedesc, H.div('return value:'),
                    retval or 'None')
        return ret

    def build_sig_value_description(self, name, _type):
        l = self.process_type_link(_type)
        items = []
        next = "%s: " % name
        for item in l:
            if isinstance(item, str):
                next += item
            else:
                if next:
                    items.append(next)
                    next = ""
                items.append(item)
        if next:
            items.append(next)
        return H.ValueDescItem(*items)

    def process_type_link(self, _type):
        # now we do simple type dispatching and provide a link in this case
        lst = []
        data = self.dsa.get_type_desc(_type)
        if not data:
            for i in _type.striter():
                if isinstance(i, str):
                    lst.append(i)
                else:
                    lst += self.process_type_link(i)
            return lst
        name, _desc_type, is_degenerated = data
        if not is_degenerated:
            linktarget = self.linker.get_lazyhref(name)
            lst.append(H.a(str(_type), href=linktarget))
        else:
            raise IOError('do not think we ever get here?')
            # we should provide here some way of linking to sourcegen directly
            lst.append(name)
        return lst

    def is_in_pkg(self, sourcefile):
        return py.path.local(sourcefile).relto(self.projpath)

    def build_callsite(self, functionname, call_site):
        tbtag = self.gen_traceback(functionname, reversed(call_site))
        return H.CallStackItem(call_site[0].filename, call_site[0].lineno + 1,
                               tbtag)
    
    _reg_source = py.std.re.compile(r'([^>]*)<(.*)>')
    def gen_traceback(self, funcname, call_site):
        tbdiv = H.div()
        for frame in call_site:
            lineno = frame.lineno - frame.firstlineno
            source = frame.source
            sourcefile = frame.filename

            tokenizer = source_color.Tokenizer(source_color.PythonSchema)
            mangled = []

            source = str(source)
            sep = get_linesep(source)
            for i, sline in enumerate(source.split(sep)):
                if i == lineno:
                    l = '-> %s' % (sline,)
                else:
                    l = '   %s' % (sline,)
                mangled.append(l)
            if sourcefile:
                linktext = '%s - line %s' % (sourcefile, frame.lineno + 1)
                # skip py.code.Source objects and source files outside of the
                # package
                is_code_source = self._reg_source.match(sourcefile)
                if (not is_code_source and self.is_in_pkg(sourcefile) and
                        py.path.local(sourcefile).check()):
                    enc = source_html.get_module_encoding(sourcefile)
                    href = self.linker.get_lazyhref(sourcefile)
                    sourcelink = H.a(linktext, href=href)
                else:
                    enc = 'latin-1'
                    sourcelink = H.div(linktext)
                colored = [enumerate_and_color(mangled,
                                               frame.firstlineno, enc)]
            else:
                sourcelink = H.div('source unknown (%s)' % (sourcefile,))
                colored = mangled[:]
            tbdiv.append(sourcelink)
            tbdiv.append(H.div(*colored))
        return tbdiv

