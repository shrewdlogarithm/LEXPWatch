from datetime import datetime
import time

print("Last Epoch Watcher Active")

import lefuncs,utils

def logname():
    return f"slot{lefuncs.lastsslot[0]}.log"

overprint = False
def addlog(log,term):
    global overprint
    if term:
        if overprint:
            print("")
            overprint = False
        endc = "\n"
    else:
        endc = "\r"
        overprint = True
    print(log,sep="",end=endc)
    try:
        with open(logname(),"a") as lf:
            lf.write(log + "\n")
    except Exception as e:
        pass # may be read-only filesystem - no matter...

def checkchar(last,slot,timenow):
    chardb = lefuncs.getchardb(slot)
    currcharname = chardb["characterName"]
    level = int(chardb["level"])
    charxp = int(chardb["currentExp"])
    mrundb={}
    for run in chardb["monolithRuns"]:
        mrundb[run["timelineID"]] = [run["stability"]]
    intvl = 0
    totalxp = 0
    if last[0] != 0:
        intvl = int((timenow-last[0]).total_seconds())
        if last[1] == level:
            totalxp = charxp-last[2]
        else:
            totalxp = lefuncs.levelxp[last[1]]-last[2]+charxp
    return currcharname,level,charxp,intvl,totalxp,mrundb

lastzone = [0,0,0]
laststab = {}
def newzone(zones):
    global lastzone,laststab
    try:
        timenow = datetime.now()
        currcharname,level,charxp,intvl,totalxp,mrundb = checkchar(lastzone,lefuncs.lastsslot[0],timenow)
        if lastzone[0] != 0 and intvl > 0:
            xppm = int(totalxp/intvl*60)
            lp = charxp/(lefuncs.levelxp[level]/100)
            pl = totalxp/intvl*60*60/lefuncs.levelxp[level]
            ts = ""
            for tlid in mrundb:
                if tlid in laststab and laststab[tlid] != mrundb[tlid]:
                    ts = f" - Timeline: {tlid} Stability change from {laststab[tlid]} to {mrundb[tlid]}"
            addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {currcharname}({level}+{lp:.1f}%) - {zones[0]:12} - {totalxp}xp in {intvl}secs = {xppm}xp/min {pl:.1f}lvl/hr {ts}",True)
            laststab = mrundb
        lastzone=[timenow,level,charxp]
    except lefuncs.FileClashException as e:
        pass # likely trying to read file whilst game is writing it
utils.addcb("zone",newzone)
newzone([])

ccxp=0
ccplaytime=0
lastchar = [0,0,0,""]
def trackchar(sslot):
    global ccxp,ccplaytime,lastchar
    try:
        timenow = datetime.now()
        currcharname,level,charxp,intvl,totalxp,mrundb = checkchar(lastchar,sslot,timenow)
        if totalxp > 0:
            if lastchar[3] != currcharname:
                ccxp=0
                ccplaytime=0
            else:
                if totalxp > 0:
                    ccxp += totalxp
                    ccplaytime += intvl
                    lp = charxp/(lefuncs.levelxp[level]/100)
                    ph = (ccxp/ccplaytime*60*60)
                    pl = ph/lefuncs.levelxp[level]
                    addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {currcharname}({level}+{lp:.1f}%) - {ph:8.0f}xp/hr {pl:.1f}lvl/hr",False)
        lastchar = [timenow,level,charxp,currcharname]
    except lefuncs.FileClashException as e:
        pass # trying to read file whilst game is writing it
utils.addcb("save",trackchar)

while lefuncs.iswatching():
    time.sleep(lefuncs.settings["quitdelay"])

print("Last Epoch Watcher Ending...")