from datetime import datetime
import time

print("Last Epoch Watcher Active")

import lefuncs,utils

def checkchar(last,slot,timenow):
    chardb = lefuncs.getchardb(slot)
    currcharname = chardb["characterName"]
    level = int(chardb["level"])
    charxp = int(chardb["currentExp"])
    intvl = 0
    totalxp = 0
    if last[0] != 0:
        intvl = int((timenow-last[0]).total_seconds())
        if last[1] == level:
            totalxp = charxp-last[2]
        else:
            totalxp = lefuncs.levelxp[last[1]]-last[2]+charxp
    return currcharname,level,charxp,intvl,totalxp

lastzone = [0,0,0]
def newzone(zone):
    global lastzone,overprint
    try:
        timenow = datetime.now()
        currcharname,level,charxp,intvl,totalxp = checkchar(lastzone,lefuncs.lastsslot[0],timenow)
        if lastzone[0] != 0 and intvl > 0:
            xppm = int(totalxp/intvl*60)
            lp = charxp/(lefuncs.levelxp[level]/100)
            pl = totalxp/intvl*60*60/lefuncs.levelxp[level]
            if overprint:
                print("\n")
                overprint = False
            print(timenow.strftime('%Y-%m-%d %H:%M:%S')," - ", zone.ljust(12," "), " - ", currcharname, "(", level, "+", "%.1f" % lp, "%) Earned ", totalxp, "xp in ", "%.2f" % intvl, "secs @", xppm, "xp/min ", "@", "%.1f" % pl,"lvl/hr",sep="")
        lastzone=[timenow,level,charxp]
    except lefuncs.FileClashException as e:
        pass # likely trying to read file whilst game is writing it
utils.addcb("zone",newzone)
newzone("Initialize")

ccxp=0
ccplaytime=0
lastchar = [0,0,0,""]
def trackchar(sslot):
    global ccxp,ccplaytime,lastchar,overprint
    try:
        timenow = datetime.now()
        currcharname,level,charxp,intvl,totalxp = checkchar(lastchar,sslot,timenow)
        if totalxp > 0:
            if lastchar[3] != currcharname:
                ccxp=0
                ccplaytime=0
            else:
                if totalxp > 0:
                    ccxp += totalxp
                    ccplaytime += intvl
                    print(timenow.strftime('%Y-%m-%d %H:%M:%S'),currcharname,ccxp,ccplaytime,"%8d" % (ccxp/ccplaytime*60*60),"xp/hr", end='\r')
                    overprint = True
        lastchar = [timenow,level,charxp,currcharname]
    except lefuncs.FileClashException as e:
        pass # trying to read file whilst game is writing it
utils.addcb("save",trackchar)

while lefuncs.iswatching():
    time.sleep(lefuncs.settings["quitdelay"])

print("Last Epoch Watcher Ending...")