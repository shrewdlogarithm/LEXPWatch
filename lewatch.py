from datetime import datetime
import lefuncs,utils

lastupd = [0,0,0]
def newzone(zone):
    global lastupd
    chardb = lefuncs.getchardb(lefuncs.getlastcharslot())
    lastcharname = chardb["characterName"]
    level = int(chardb["level"])
    charxp = int(chardb["currentExp"])
    totalxp = 0
    xppm = 0
    if lastupd[0] != 0:
        if lastupd[1] == level:
            totalxp = charxp-lastupd[2]
        else:
            totalxp = lefuncs.levelxp[lastupd[1]]-lastupd[2]+charxp
        intvl = (datetime.now()-lastupd[0]).total_seconds()
        xppm = int(totalxp/intvl*60)
        lp = charxp/(lefuncs.levelxp[level]/100)
        pl = totalxp/(lefuncs.levelxp[level])/intvl*60*60
        print(zone.ljust(12," "), " - ", lastcharname, "(", level, "+", "%.1f" % lp, "%) Earned ", totalxp, "xp in ", "%.2f" % intvl, "secs @", xppm, "xp/min ", "@", "%.1f" % pl,"lvl/hr",sep="")
    lastupd=[datetime.now(),level,charxp]

utils.addcb("zone",newzone)
newzone("Initialize")

print("Last Epoch Watcher Active")

while lefuncs.iswatching():
    pass