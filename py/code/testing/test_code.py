from __future__ import generators
import py

def test_newcode(): 
    source = "i = 3"
    co = compile(source, '', 'exec') 
    code = py.code.Code(co) 
    newco = code.new() 
    assert co == newco 

def test_ne():
    code1 = py.code.Code(compile('foo = "bar"', '', 'exec'))
    assert code1 == code1
    code2 = py.code.Code(compile('foo = "baz"', '', 'exec'))
    assert code2 != code1

def test_newcode_unknown_args(): 
    code = py.code.Code(compile("", '', 'exec'))
    py.test.raises(TypeError, 'code.new(filename="hello")')

def test_newcode_withfilename():
    source = py.code.Source("""
        def f():
            def g():
                pass
    """)
    co = compile(str(source)+'\n', 'nada', 'exec')
    obj = 'hello'
    newco = py.code.Code(co).new(rec=True, co_filename=obj)
    def walkcode(co):
        for x in co.co_consts:
            if isinstance(x, type(co)):
                for y in walkcode(x):
                    yield y
        yield co

    names = []
    for code in walkcode(newco):
        assert newco.co_filename == obj
        assert newco.co_filename is obj
        names.append(code.co_name)
    assert 'f' in names
    assert 'g' in names

def test_newcode_with_filename(): 
    source = "i = 3"
    co = compile(source, '', 'exec') 
    code = py.code.Code(co) 
    class MyStr(str): 
        pass 
    filename = MyStr("hello") 
    filename.__source__ = py.code.Source(source) 
    newco = code.new(rec=True, co_filename=filename) 
    assert newco.co_filename is filename 
    s = py.code.Source(newco) 
    assert str(s) == source 

