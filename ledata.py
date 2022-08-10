import os,glob,re

def lepath():
    path = os.getenv("USERPROFILE") # should be the Windows AND Linux base path - Linux untested tho...
    if path: # we're on Windows
        return path + "/appdata/locallow/"
    else: # almost certainly Linux as LE doesn't run on OSX??
        return os.getenv("HOME") + "/.config/unity3d/" # this is untested as yet - I'm guessing at the Linux path here...

# Find last played character slot
def findlastsslot(path): 
    mrecent = 0
    mrfile = "0"
    slotfiles = glob.glob(path + "Saves/1*")
    for slotfile in slotfiles:
        mtime = os.path.getmtime(slotfile)
        if mtime > mrecent:
            mrecent = mtime
            mrfile = slotfile    
    if mrfile != "0":
        return re.findall(r'\d+', mrfile)[-1]
    else:
        return None
        
# Return saveslot file (testchar.txt used for testing without the game running/installed)
def filenameforslot(path,sslot):
    if os.path.exists("testchar.txt"):
        return "testchar.txt"
    else:
        return path + "/Saves/1CHARACTERSLOT_BETA_" + sslot    

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