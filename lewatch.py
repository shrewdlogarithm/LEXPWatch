from datetime import datetime
import time
import lefuncs,utils

xpearned = 0
timeplayed = 0

lastzone = [0,0,0]
def newzone(zone):
    global lastzone
    #time.sleep(2) TODO - the save file isn't updated until quite a while after zoning - perhaps we just trigger this elsewhere?
    chardb = lefuncs.getchardb(lefuncs.getlastcharslot())
    currcharname = chardb["characterName"]
    level = int(chardb["level"])
    charxp = int(chardb["currentExp"])
    totalxp = 0
    timenow = datetime.now()
    if lastzone[0] != 0:
        intvl = int((timenow-lastzone[0]).total_seconds())
        if lastzone[1] == level:
            totalxp = charxp-lastzone[2]
        else:
            totalxp = lefuncs.levelxp[lastzone[1]]-lastzone[2]+charxp
        xppm = int(totalxp/intvl*60)
        lp = charxp/(lefuncs.levelxp[level]/100)
        pl = totalxp/intvl*60*60/lefuncs.levelxp[level]
        print(timenow.strftime('%Y-%m-%d %H:%M:%S')," - ", zone.ljust(12," "), " - ", currcharname, "(", level, "+", "%.1f" % lp, "%) Earned ", totalxp, "xp in ", "%.2f" % intvl, "secs @", xppm, "xp/min ", "@", "%.1f" % pl,"lvl/hr",sep="")
    lastzone=[timenow,level,charxp]

utils.addcb("zone",newzone)
newzone("Initialize")

print("Last Epoch Watcher Active")

ccxp=0
ccplaytime=0
lastchar = [0,0,0,""]
while lefuncs.iswatching():
    chardb = lefuncs.getchardb(lefuncs.getlastcharslot())
    currcharname = chardb["characterName"]
    level = int(chardb["level"])
    charxp = int(chardb["currentExp"])
    totalxp = 0
    timenow = datetime.now()
    if lastchar[0] != 0:
        intvl = int((timenow-lastchar[0]).total_seconds())
        if lastchar[1] == level:
            totalxp = charxp-lastchar[2]
        else:
            totalxp = lefuncs.levelxp[lastchar[1]]-lastchar[2]+charxp        
        if lastchar[3] != currcharname:
            ccxp=0
            ccplaytime=0
        else:
            if totalxp > 0:
                ccxp += totalxp
                ccplaytime += intvl
                print(timenow.strftime('%Y-%m-%d %H:%M:%S'),currcharname,ccxp,ccplaytime,"%8d" % (ccxp/ccplaytime*60*60),"xp/hr")
    lastchar = [timenow,level,charxp,currcharname]
    time.sleep(10)