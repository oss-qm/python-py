from py.__.test.dsession.dsession import DSession, LoopState
from py.__.test.dsession.hostmanage import Host, makehostup
from py.__.test.runner import basic_collect_report 
from py.__.test import event
from py.__.test import outcome
import py

def run(item):
    runner = item._getrunner()
    return runner(item)

class MockNode:
    def __init__(self):
        self.sent = []

    def sendlist(self, items):
        self.sent.append(items)

    def shutdown(self):
        self._shutdown=True

def dumpqueue(queue):
    while queue.qsize():
        print queue.get()

class TestDSession:
    def test_fixoptions(self, testdir):
        config = testdir.parseconfig("--exec=xxx")
        config.pytestplugins.configure(config)
        config.initsession().fixoptions()
        assert config.option.numprocesses == 1
        config = testdir.parseconfig("--exec=xxx", '-n3')
        config.initsession().fixoptions()
        assert config.option.numprocesses == 3

    def test_add_remove_host(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        rep = run(item)
        session = DSession(item._config)
        host = Host("localhost")
        host.node = MockNode()
        assert not session.host2pending
        session.addhost(host)
        assert len(session.host2pending) == 1
        session.senditems([item])
        pending = session.removehost(host)
        assert pending == [item]
        assert item not in session.item2host
        py.test.raises(Exception, "session.removehost(host)")

    def test_senditems_removeitems(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        rep = run(item)
        session = DSession(item._config)
        host = Host("localhost")
        host.node = MockNode()
        session.addhost(host)
        session.senditems([item])  
        assert session.host2pending[host] == [item]
        assert session.item2host[item] == host
        session.removeitem(item)
        assert not session.host2pending[host] 
        assert not session.item2host

    def test_triggertesting_collect(self, testdir):
        modcol = testdir.getmodulecol("""
            def test_func():
                pass
        """)
        session = DSession(modcol._config)
        session.triggertesting([modcol])
        name, args, kwargs = session.queue.get(block=False)
        assert name == 'collectionreport'
        rep, = args 
        assert len(rep.result) == 1

    def test_triggertesting_item(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        host2 = Host("localhost")
        host2.node = MockNode()
        session.addhost(host1)
        session.addhost(host2)
        session.triggertesting([item] * (session.MAXITEMSPERHOST*2 + 1))
        host1_sent = host1.node.sent[0]
        host2_sent = host2.node.sent[0]
        assert host1_sent == [item] * session.MAXITEMSPERHOST
        assert host2_sent == [item] * session.MAXITEMSPERHOST
        assert session.host2pending[host1] == host1_sent
        assert session.host2pending[host2] == host2_sent
        name, args, kwargs = session.queue.get(block=False)
        assert name == "rescheduleitems"
        ev, = args 
        assert ev.items == [item]

    def test_keyboardinterrupt(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
        def raise_(timeout=None): raise KeyboardInterrupt()
        session.queue.get = raise_
        exitstatus = session.loop([])
        assert exitstatus == outcome.EXIT_INTERRUPTED

    def test_internalerror(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
        def raise_(): raise ValueError()
        session.queue.get = raise_
        exitstatus = session.loop([])
        assert exitstatus == outcome.EXIT_INTERNALERROR

    def test_rescheduleevent(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        session.addhost(host1)
        ev = event.RescheduleItems([item])
        loopstate = LoopState([])
        session.queueevent("rescheduleitems", ev)
        session.loop_once(loopstate)
        # check that RescheduleEvents are not immediately
        # rescheduled if there are no hosts 
        assert loopstate.dowork == False 
        session.queueevent("anonymous", event.NOP())
        session.loop_once(loopstate)
        session.queueevent("anonymous", event.NOP())
        session.loop_once(loopstate)
        assert host1.node.sent == [[item]]
        session.queueevent("itemtestreport", run(item))
        session.loop_once(loopstate)
        assert loopstate.shuttingdown 
        assert not loopstate.testsfailed 

    def test_no_hosts_remaining_for_tests(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        # setup a session with one host
        session = DSession(item._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        session.addhost(host1)
       
        # setup a HostDown event
        ev = event.HostDown(host1, None)
        session.queueevent("hostdown", ev)

        loopstate = LoopState([item])
        loopstate.dowork = False
        session.loop_once(loopstate)
        dumpqueue(session.queue)
        assert loopstate.exitstatus == outcome.EXIT_NOHOSTS

    def test_hostdown_causes_reschedule_pending(self, testdir, EventRecorder):
        modcol = testdir.getmodulecol("""
            def test_crash(): 
                assert 0
            def test_fail(): 
                x
        """)
        item1, item2 = modcol.collect()

        # setup a session with two hosts 
        session = DSession(item1._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        session.addhost(host1)
        host2 = Host("localhost")
        host2.node = MockNode()
        session.addhost(host2)
      
        # have one test pending for a host that goes down 
        session.senditems([item1, item2])
        host = session.item2host[item1]
        ev = event.HostDown(host, None)
        session.queueevent("hostdown", ev)
        evrec = EventRecorder(session.bus)
        loopstate = LoopState([])
        session.loop_once(loopstate)

        assert loopstate.colitems == [item2] # do not reschedule crash item
        testrep = evrec.getfirstnamed("itemtestreport")
        assert testrep.failed
        assert testrep.colitem == item1
        assert str(testrep.longrepr).find("crashed") != -1
        assert str(testrep.longrepr).find(host.hostname) != -1

    def test_hostup_adds_to_available(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        # setup a session with two hosts 
        session = DSession(item._config)
        host1 = Host("localhost")
        hostup = makehostup(host1)
        session.queueevent("hostup", hostup)
        loopstate = LoopState([item])
        loopstate.dowork = False
        assert len(session.host2pending) == 0
        session.loop_once(loopstate)
        assert len(session.host2pending) == 1

    def test_event_propagation(self, testdir, EventRecorder):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
      
        evrec = EventRecorder(session.bus)
        session.queueevent("NOPevent", 42)
        session.loop_once(LoopState([]))
        assert evrec.getfirstnamed('NOPevent')

    def runthrough(self, item):
        session = DSession(item._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        session.addhost(host1)
        loopstate = LoopState([item])

        session.queueevent("NOP")
        session.loop_once(loopstate)

        assert host1.node.sent == [[item]]
        ev = run(item)
        session.queueevent("itemtestreport", ev)
        session.loop_once(loopstate)
        assert loopstate.shuttingdown  
        session.queueevent("hostdown", event.HostDown(host1, None))
        session.loop_once(loopstate)
        dumpqueue(session.queue)
        return session, loopstate.exitstatus 

    def test_exit_completed_tests_ok(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session, exitstatus = self.runthrough(item)
        assert exitstatus == outcome.EXIT_OK

    def test_exit_completed_tests_fail(self, testdir):
        item = testdir.getitem("def test_func(): 0/0")
        session, exitstatus = self.runthrough(item)
        assert exitstatus == outcome.EXIT_TESTSFAILED

    def test_exit_on_first_failing(self, testdir):
        modcol = testdir.getmodulecol("""
            def test_fail(): 
                assert 0
            def test_pass(): 
                pass
        """)
        modcol._config.option.exitfirst = True
        session = DSession(modcol._config)
        host1 = Host("localhost")
        host1.node = MockNode()
        session.addhost(host1)
        items = basic_collect_report(modcol).result

        # trigger testing  - this sends tests to host1
        session.triggertesting(items)

        # run tests ourselves and produce reports 
        ev1 = run(items[0])
        ev2 = run(items[1])
        session.queueevent("itemtestreport", ev1) # a failing one
        session.queueevent("itemtestreport", ev2)
        # now call the loop
        loopstate = LoopState(items)
        session.loop_once(loopstate)
        assert loopstate.testsfailed
        assert loopstate.shuttingdown

    def test_shuttingdown_filters_events(self, testdir, EventRecorder):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)
        host = Host("localhost")
        session.addhost(host)
        loopstate = LoopState([])
        loopstate.shuttingdown = True
        evrec = EventRecorder(session.bus)
        session.queueevent("itemtestreport", run(item))
        session.loop_once(loopstate)
        assert not evrec.getfirstnamed("hostdown")
        ev = event.HostDown(host)
        session.queueevent("hostdown", ev)
        session.loop_once(loopstate)
        assert evrec.getfirstnamed('hostdown') == ev

    def test_filteritems(self, testdir, EventRecorder):
        modcol = testdir.getmodulecol("""
            def test_fail(): 
                assert 0
            def test_pass(): 
                pass
        """)
        session = DSession(modcol._config)

        modcol._config.option.keyword = "nothing"
        dsel = session.filteritems([modcol])
        assert dsel == [modcol] 
        items = modcol.collect()
        evrec = EventRecorder(session.bus)
        remaining = session.filteritems(items)
        assert remaining == []
        
        evname, ev = evrec.events[-1]
        assert evname == "deselected"
        assert ev.items == items 

        modcol._config.option.keyword = "test_fail"
        remaining = session.filteritems(items)
        assert remaining == [items[0]]

        evname, ev = evrec.events[-1]
        assert evname == "deselected"
        assert ev.items == [items[1]]

    def test_hostdown_shutdown_after_completion(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        session = DSession(item._config)

        host = Host("localhost")
        host.node = MockNode()
        session.addhost(host)
        session.senditems([item])
        session.queueevent("itemtestreport", run(item))
        loopstate = LoopState([]) 
        session.loop_once(loopstate)
        assert host.node._shutdown is True
        assert loopstate.exitstatus is None, "loop did not wait for hostdown"
        assert loopstate.shuttingdown 
        session.queueevent("hostdown", event.HostDown(host, None))
        session.loop_once(loopstate)
        assert loopstate.exitstatus == 0

    def test_nopending_but_collection_remains(self, testdir):
        modcol = testdir.getmodulecol("""
            def test_fail(): 
                assert 0
            def test_pass(): 
                pass
        """)
        session = DSession(modcol._config)
        host = Host("localhost")
        host.node = MockNode()
        session.addhost(host)

        colreport = basic_collect_report(modcol)
        item1, item2 = colreport.result
        session.senditems([item1])
        # host2pending will become empty when the loop sees
        # the report 
        session.queueevent("itemtestreport", run(item1)) 

        # but we have a collection pending
        session.queueevent("collectionreport", colreport) 

        loopstate = LoopState([]) 
        session.loop_once(loopstate)
        assert loopstate.exitstatus is None, "loop did not care for collection report"
        assert not loopstate.colitems 
        session.loop_once(loopstate)
        assert loopstate.colitems == colreport.result
        assert loopstate.exitstatus is None, "loop did not care for colitems"
