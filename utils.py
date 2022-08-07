import threading,json

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

def loadjson(file,offset=0):
    data = "{}"
    try:
        with open(file,"r") as f:
            data = f.read()[offset:]
    except Exception as e:
        pass # may not yet exist
    return json.loads(data)
        
def savejson(file,data):
    with open(file,"w") as f:
        json.dump(data,f,indent=4)