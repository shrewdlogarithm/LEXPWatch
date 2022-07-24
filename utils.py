import threading

# Thread decorator
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func

# Callback Manager
cbdb = {}
def addcb(typ,fn):
    if typ not in cbdb:
        cbdb[typ] = []
    cbdb[typ].append(fn)
def runcb(typ,para):
    if typ in cbdb:
        for f in cbdb[typ]:
            f(para)