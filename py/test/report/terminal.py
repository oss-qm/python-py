import py
import sys
from py.__.test import event
from py.__.test.report.base import BaseReporter
from py.__.test.report.base import getrelpath, repr_pythonversion

class TerminalReporter(BaseReporter):
    def __init__(self, config, file=None, bus=None):
        super(TerminalReporter, self).__init__(bus=bus)
        self.config = config
        self.curdir = py.path.local()
        if file is None:
            file = py.std.sys.stdout
        self._tw = py.io.TerminalWriter(file)

    def _reset(self):
        self.currentfspath = None 
        super(TerminalReporter, self)._reset()

    def write_fspath_result(self, fspath, res):
        if fspath != self.currentfspath:
            self._tw.line()
            relpath = getrelpath(self.curdir, fspath)
            self._tw.write(relpath + " ")
            self.currentfspath = fspath
        self._tw.write(res)

    def write_ensure_prefix(self, prefix, extra=""):
        if self.currentfspath != prefix:
            self._tw.line()
            self.currentfspath = prefix 
            self._tw.write(prefix)
        if extra:
            self._tw.write(extra)
            self.currentfspath = -2

    def ensure_newline(self):
        if self.currentfspath: 
            self._tw.line()
            self.currentfspath = None

    def write_line(self, line, **markup):
        line = str(line)
        self.ensure_newline()
        self._tw.line(line, **markup)

    def write_sep(self, sep, title=None, **markup):
        self.ensure_newline()
        self._tw.sep(sep, title, **markup)

    def getoutcomeword(self, item):
        if item.passed: return self._tw.markup("PASS", green=True)
        elif item.failed: return self._tw.markup("FAIL", red=True)
        elif item.skipped: return "SKIP"
        else: return self._tw.markup("???", red=True)

    def rep_InternalException(self, ev):
        for line in str(ev.repr).split("\n"):
            self.write_line("InternalException: " + line)

    def rep_HostGatewayReady(self, ev):
        if self.config.option.verbose:
            self.write_line("HostGatewayReady: %s" %(ev.host,))

    def rep_HostUp(self, ev):
        d = ev.platinfo.copy()
        d['hostid'] = ev.host.hostid
        d['version'] = repr_pythonversion(d['sys.version_info'])
        self.write_line("HOSTUP: %(hostid)s %(sys.platform)s "
                      "%(sys.executable)s - Python %(version)s" %
                      d)

    def rep_HostDown(self, ev):
        host = ev.host
        error = ev.error
        if error:
            self.write_line("HostDown %s: %s" %(host.hostid, error))

    def rep_ItemStart(self, ev):
        if self.config.option.verbose:
            info = ev.item.repr_metainfo()
            line = info.verboseline(basedir=self.curdir) + " "
            extra = ""
            if ev.host:
                extra = "-> " + ev.host.hostid
            self.write_ensure_prefix(line, extra)

    def rep_RescheduleItems(self, ev):
        if self.config.option.debug:
            self.write_sep("!", "RESCHEDULING %s " %(ev.items,))
    
    def rep_ItemTestReport(self, ev):
        super(TerminalReporter, self).rep_ItemTestReport(ev)
        fspath = ev.colitem.fspath 
        if not self.config.option.verbose:
            self.write_fspath_result(fspath, ev.outcome.shortrepr)
        else:
            info = ev.colitem.repr_metainfo()
            line = info.verboseline(basedir=self.curdir) + " "
            word = self.getoutcomeword(ev)
            self.write_ensure_prefix(line, word)

    def rep_CollectionReport(self, ev):
        super(TerminalReporter, self).rep_CollectionReport(ev)
        fspath = ev.colitem.fspath 
        if ev.failed or ev.skipped:
            if ev.skipped:
                msg = ev.outcome.longrepr.message
            else:
                msg = ev.outcome.longrepr.reprcrash.message
            self.write_fspath_result(fspath, "- " + str(msg))

    def rep_TestrunStart(self, ev):
        super(TerminalReporter, self).rep_TestrunStart(ev)
        self.write_sep("=", "test session starts", bold=True)
        self._sessionstarttime = py.std.time.time()
        #self.out_hostinfo()

    def rep_TestrunFinish(self, ev):
        self._tw.line("")
        if ev.exitstatus == 0 or ev.exitstatus == 1:
            self.summary_failures()
            self.summary_skips()
        elif ev.exitstatus == 2:
            self.write_sep("!", "KEYBOARD INTERRUPT")
        self.summary_deselected()
        self.summary_stats()

    def rep_LooponfailingInfo(self, ev):
        if ev.failreports:
            self.write_sep("#", "LOOPONFAILING", red=True)
            for report in ev.failreports:
                try:
                    loc = report.outcome.longrepr.reprcrash
                except AttributeError:
                    loc = str(report.outcome.longrepr)[:50]
                self.write_line(loc, red=True)
        self.write_sep("#", "waiting for changes")
        for rootdir in ev.rootdirs:
            self.write_line("### Watching:   %s" %(rootdir,), bold=True)

        if 0:
            print "#" * 60
            print "# looponfailing: mode: %d failures args" % len(failures)
            for ev in failurereports:
                name = "/".join(ev.colitem.listnames()) # XXX
                print "Failure at: %r" % (name,) 
            print "#    watching py files below %s" % rootdir
            print "#                           ", "^" * len(str(rootdir))
            failures = [ev.colitem for ev in failurereports]
            if not failures:
                failures = colitems 

    #
    # summaries for TestrunFinish 
    #

    def summary_failures(self):
        if self._failed:
            self.write_sep("=", "FAILURES")
            for ev in self._failed:
                self.write_sep("_")
                ev.toterminal(self._tw)

    def summary_stats(self):
        session_duration = py.std.time.time() - self._sessionstarttime
        numfailed = len(self._failed)
        numskipped = len(self._skipped)
        numpassed = len(self._passed)
        sum = numfailed + numpassed
        self.write_sep("=", "%d/%d passed + %d skips in %.2f seconds" %
                      (numpassed, sum, numskipped, session_duration), bold=True)
        if numfailed == 0:
            self.write_sep("=", "failures: no failures :)", green=True)
        else:
            self.write_sep("=", "failures: %d" %(numfailed), red=True)

    def summary_deselected(self):
        if not self._deselected:
            return
        self.write_sep("=", "%d tests deselected by %r" %(
            len(self._deselected), self.config.option.keyword), bold=True)
                                                

    def summary_skips(self):
        if not self._failed or self.config.option.showskipsummary:
            folded_skips = self._folded_skips()
            if folded_skips:
                self.write_sep("_", "skipped test summary")
                for num, fspath, lineno, reason in folded_skips:
                    self._tw.line("%s:%d: [%d] %s" %(fspath, lineno, num, reason))

    def out_hostinfo(self):
        self._tw.line("host 0: %s %s - Python %s" %
                       (py.std.sys.platform, 
                        py.std.sys.executable, 
                        repr_pythonversion()))

Reporter = TerminalReporter 
