import py
html = py.xml.html

def getrelfspath(dotted_name):
    # XXX need to make sure its imported on non-py lib 
    return eval(dotted_name, {"py": py})

class LazyHref(object):
    def __init__(self, linker, linkid):
        self._linker = linker
        self._linkid = linkid

    def __unicode__(self):
        return unicode(self._linker.get_target(self._linkid))

class Linker(object):
    fromlocation = None

    def __init__(self):
        self._linkid2target = {}

    def get_lazyhref(self, linkid):
        return LazyHref(self, linkid)

    def set_link(self, linkid, target):
        assert (linkid not in self._linkid2target,
                'linkid %r already used' % (linkid,))
        self._linkid2target[linkid] = target

    def get_target(self, linkid):
        linktarget = self._linkid2target[linkid]
        if self.fromlocation is not None:
            linktarget = relpath(self.fromlocation, linktarget)
        return linktarget

    def call_withbase(self, base, func, *args, **kwargs):
        assert self.fromlocation is None
        self.fromlocation = base 
        try:
            return func(*args, **kwargs)
        finally:
            del self.fromlocation 
    
def relpath(p1, p2, sep='/', back='..'):
    if (p1.startswith(sep) ^ p2.startswith(sep)): 
        raise ValueError("mixed absolute relative path: %r -> %r" %(p1, p2))
    fromlist = p1.split(sep)
    tolist = p2.split(sep)

    # AA
    # AA BB     -> AA/BB
    #
    # AA BB
    # AA CC     -> CC
    #
    # AA BB 
    # AA      -> ../AA

    diffindex = 0
    for x1, x2 in zip(fromlist, tolist):
        if x1 != x2:
            break
        diffindex += 1
    commonindex = diffindex - 1

    fromlist_diff = fromlist[diffindex:]
    tolist_diff = tolist[diffindex:]

    if not fromlist_diff:
        return sep.join(tolist[commonindex:])
    backcount = len(fromlist_diff)
    if tolist_diff:
        return sep.join([back,]*(backcount-1) + tolist_diff)
    return sep.join([back,]*(backcount) + tolist[commonindex:])

