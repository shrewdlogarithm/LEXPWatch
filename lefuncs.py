import glob,os,json,re,time
import utils

watching=True

# Load/Initialize Settings
path = os.getenv("USERPROFILE")
if path: # Windows
    path = path + "/appdata/locallow/"
else:
    path = os.getenv("HOME") + "/.config/unity3d/"
settings = {
        "ledir": path + "/Eleventh Hour Games/Last Epoch/",
        "zonedelay": 5,
        "savedelay": 5,
        "quitdelay": 5
}      
try:
    with open("settings.json","r") as f:
        settings = {**settings,**json.load(f)}
except Exception as e:
    pass
        
def save_settings():
    with open("settings.json","w") as f:
        json.dump(settings,f,indent=4)
save_settings()

testfile = False
if os.path.exists("testchar.txt"):
    testfile = True
def getsavefile(sslot):
    if testfile:
        return "testchar.txt"
    else:
        return settings["ledir"] + "/Saves/1CHARACTERSLOT_BETA_" + sslot    

class FileClashException(Exception):
    def __init__(self, message='Key Empty'):
        super(FileClashException, self).__init__(message)

# Load character data from savefile for slot
def getchardb(sslot):
    chardb={}
    try:
        savefile = getsavefile(sslot)
        with open(savefile,"r") as f:
            listo = f.read()[5:]
            chardb = json.loads(listo)    
            return chardb
    except Exception as e:        
        raise FileClashException(f"Failed to read saveslot {sslot}")

# Find last played character slot
lastsslot = ["0",0]
def checklastsslot(): 
    global lastsslot,watching
    mrecent = 0
    mrfile = "0"
    f = glob.glob(settings["ledir"] + "Saves/1*")
    for fl in f:
        mtime = os.path.getmtime(fl)
        if mtime > mrecent:
            mrecent = mtime
            mrfile = fl    
    if mrfile != "0":
        lastsslot = [re.findall(r'\d+', mrfile)[-1],mrecent]
    else:
        print("Cannot find any character saves - check path in settings.json")
        watching = False
checklastsslot()

# Monitor Log and Save Files
def iswatching():
    return watching
@utils.background
def watchlog():
    global watching
    firstime = True
    sline = 0
    logfile = "testlog.txt"
    if not os.path.exists(logfile): # local debug file
        logfile = settings["ledir"] + "Player.log"
    while watching:
        try:
            with open(logfile,"r") as f:
                f.seek(0,2) # goto EOF
                if f.tell() < sline: # file shorter than at last check 
                    sline = 0 # reset to start
                f.seek(sline,0) # goto last read position
                nlines = f.readlines() # read any new content
                if not firstime: # we ignore what was in the file before this program was run
                    for ln in nlines:
                        op = ln.strip() # remove newlines etc.
                        if len(op) > 0: # ignore blanklines                            
                            utils.runcb("log",op)
                else:
                    firstime = False
                sline = f.tell() # move pointer to EOF
                time.sleep(settings["zonedelay"])
        except Exception as e:
            print("Error in watchlog",e,type(e))
            time.sleep(1)
watchlog() 

@utils.background
def watchsave():
    global watching
    try:
        lastupd = 0
        while watching:
            if lastsslot[0] != "0":
                upd = os.stat(getsavefile(lastsslot[0])).st_mtime
                if upd != lastupd:
                    utils.runcb("save",lastsslot[0])
                lastupd = upd            
    except Exception as e:
        print("Error in watchsave",e,type(e))
    time.sleep(settings["savedelay"])
watchsave()

# Handle zone changes
lastzone = "Unknown"
def checkzonechange(l):
    global lastzone
    zc = re.match(r'Loading Scene(.*)', l)
    if zc:
        lastzone = zc.group(1).strip()
        checklastsslot()
        utils.runcb("zone",lastzone)
    else:
        pass
utils.addcb("log",checkzonechange)

# Level XP Table
levelxp = [
    0,
    77,
    161,
    261,
    380,
    517,
    674,
    851,
    1051,
    1273,
    1520,
    1789,
    2086,
    2408,
    2759,
    3137,
    3545,
    3984,
    4455,
    4958,
    5496,
    6067,
    6678,
    7325,
    8014,
    8744,
    9519,
    10341,
    11214,
    12140,
    13126,
    14173,
    15291,
    16486,
    17766,
    19142,
    20623,
    22225,
    23964,
    25857,
    27926,
    30196,
    32697,
    35460,
    38525,
    41935,
    45740,
    49997,
    54771,
    60135,
    66174,
    72978,
    80655,
    89324,
    99117,
    110184,
    122690,
    136820,
    152782,
    170804,
    191141,
    214069,
    239905,
    268986,
    301692,
    338435,
    379672,
    425900,
    477667,
    535569,
    600260,
    672448,
    752912,
    842493,
    942110,
    1052755,
    1175509,
    1311538,
    1462109,
    1628587,
    1812451,
    2015289,
    2238822,
    2484895,
    2755498,
    3052768,
    3379000,
    3736658,
    4128384,
    4557007,
    5025556,
    5537270,
    6095617,
    6704292,
    7367248,
    8088694,
    8873121,
    9725312,
    10650357,
    11653669
]