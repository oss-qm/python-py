
import py
import example1

from py.__.test.rsession.executor import RunExecutor, BoxExecutor,\
    AsyncExecutor, ApigenExecutor
from py.__.test.rsession.outcome import ReprOutcome
from py.__.test.rsession.testing.runtest import BasicRsessionTest

#def setup_module(mod):
#    mod.rootdir = py.path.local(py.__file__).dirpath().dirpath()
#    mod.config = py.test.config._reparse([mod.rootdir])

class ItemTestPassing(py.test.Item):    
    def run(self):
        return None

class ItemTestFailing(py.test.Item):
    def run(self):
        assert 0 == 1

class ItemTestSkipping(py.test.Item):
    def run(self):
        py.test.skip("hello")

class TestExecutor(BasicRsessionTest):
    def test_run_executor(self):
        ex = RunExecutor(ItemTestPassing("pass"), config=self.config)
        outcome = ex.execute()
        assert outcome.passed
    
        ex = RunExecutor(ItemTestFailing("fail"), config=self.config)
        outcome = ex.execute()
        assert not outcome.passed

        ex = RunExecutor(ItemTestSkipping("skip"), config=self.config)
        outcome = ex.execute()
        assert outcome.skipped 
        assert not outcome.passed
        assert not outcome.excinfo 

    def test_box_executor(self):
        ex = BoxExecutor(ItemTestPassing("pass"), config=self.config)
        outcome_repr = ex.execute()
        outcome = ReprOutcome(outcome_repr)
        assert outcome.passed
    
        ex = BoxExecutor(ItemTestFailing("fail"), config=self.config)
        outcome_repr = ex.execute()
        outcome = ReprOutcome(outcome_repr)
        assert not outcome.passed

        ex = BoxExecutor(ItemTestSkipping("skip"), config=self.config)
        outcome_repr = ex.execute()
        outcome = ReprOutcome(outcome_repr)
        assert outcome.skipped 
        assert not outcome.passed
        assert not outcome.excinfo 

    def test_box_executor_stdout(self):
        item = self.rootcol._getitembynames(self.funcprint_spec)
        ex = BoxExecutor(item, config=self.config)
        outcome_repr = ex.execute()
        outcome = ReprOutcome(outcome_repr)
        assert outcome.passed
        assert outcome.stdout.find("samfing") != -1

    def test_box_executor_stdout_error(self):
        item = self.rootcol._getitembynames(self.funcprintfail_spec)
        ex = BoxExecutor(item, config=self.config)
        outcome_repr = ex.execute()
        outcome = ReprOutcome(outcome_repr)
        assert not outcome.passed
        assert outcome.stdout.find("samfing elz") != -1 

    def test_cont_executor(self):
        item = self.rootcol._getitembynames(self.funcprintfail_spec)
        ex = AsyncExecutor(item, config=self.config)
        cont, pid = ex.execute()
        assert pid
        outcome_repr = cont()
        outcome = ReprOutcome(outcome_repr)
        assert not outcome.passed
        assert outcome.stdout.find("samfing elz") != -1

    def test_apigen_executor(self):
        class Tracer(object):
            def __init__(self):
                self.starts = 0
                self.ends = 0
        
            def start_tracing(self):
                self.starts += 1

            def end_tracing(self):
                self.ends += 1
    
        tmpdir = py.test.ensuretemp("apigen_executor")
        tmpdir.ensure("__init__.py")
        tmpdir.ensure("test_one.py").write(py.code.Source("""
        def g():
            pass
    
        def test_1():
            g()

        class TestX(object):
            def setup_method(self, m):
                self.ttt = 1

            def test_one(self):
                self.ttt += 1

            def test_raise(self):
                1/0
        """))
        config = py.test.config._reparse([tmpdir])
        rootcol = config._getcollector(tmpdir)
        tracer = Tracer()
        item = rootcol._getitembynames("test_one.py/test_1")
        ex = ApigenExecutor(item, config=config)
        out1 = ex.execute(tracer)
        item = rootcol._getitembynames("test_one.py/TestX/()/test_one")
        ex = ApigenExecutor(item, config=config)
        out2 = ex.execute(tracer)
        item = rootcol._getitembynames("test_one.py/TestX/()/test_raise")
        ex = ApigenExecutor(item, config=config)
        out3 = ex.execute(tracer)
        assert tracer.starts == 3
        assert tracer.ends == 3
        assert out1.passed
        assert out2.passed
        assert not out3.passed
