# Converted to OO and NOT YET FULLY TESTED

import time,os,re,utils,ledata,settings
from datetime import datetime

class FileClashException(Exception):
    def __init__(self, message='Key Empty'):
        super(FileClashException, self).__init__(message)

class CharData: # returned by checkchar - used in monitoring
    playtime = 0
    earnedxp = 0
    stabDB = {}
    def __init__(self,chardb):        
        self.charname = chardb["characterName"]
        self.level = int(chardb["level"])
        self.xp = int(chardb["currentExp"])
        for run in chardb["monolithRuns"]:
            self.stabDB[run["timelineID"]] = [run["stability"]]

class LastCheck: # how we check for changes
    def __init__(self):
        self.time = 0
        self.chardata = {}        
    def update(self,time,chardata:CharData):
        self.time = time
        self.chardata = chardata

class CharPlayed: # accumulate player 'earnings' and calculate progress
    def __init__(self):
        self.xp = 0
        self.time = 0
    def update(self,chardata:CharData):
        self.xp += chardata.earnedxp
        self.time += chardata.playtime
        self.perclevel = chardata.earnedxp/(ledata.levelxp[chardata.level]/100) 
        self.xpperhour = (self.xp/self.time*60*60) 
        self.levelperhour = self.xpperhour/ledata.levelxp[chardata.level] 

class LEWatch:
    def __init__(self):
        self.watching=True
               
        # Default Settings
        settings.load({
            "ledir": ledata.lepath() + "/Eleventh Hour Games/Last Epoch/",
            "zonedelay": 5,
            "savedelay": 5,
            "quitdelay": 5
        },"settings.json")

        self.lastsslot = ledata.findlastsslot(settings.get("ledir")) 

    # Output to file/console
    overprint = False    
    def addlog(self,log,term):
        if term:
            if self.overprint:
                print("") # close the overwritten line
                self.overprint = False
            endc = "\n"
        else:
            endc = "\r"
            self.overprint = True
        print(log,sep="",end=endc)
        try:
            with open(f"slot{self.lastsslot}.log","a") as lf:
                lf.write(log + "\n")
        except Exception as e:
            pass # may be read-only filesystem - no matter... 

    # Handle zone changes
    lastzonename = "Unknown"
    def checkzonechange(self,l):
        zc = re.match(r'Loading Scene(.*)', l)
        if zc:
            zones = [self.lastzonename,zc.group(1).strip()]
            self.lastzonename = zc.group(1).strip()
            self.lastsslot = ledata.findlastsslot(settings.get("ledir"))
            utils.runcb("zone",zones)

    # Handle ongolng XP calculation
    def checkchar(self,last:LastCheck,slot,timenow) -> CharData:
        try:
            chardata = CharData(utils.loadjson(ledata.filenameforslot(settings.get("ledir"),slot),5))
            if last.time != 0:
                chardata.playtime = int((timenow-last.time).total_seconds())
                if last.chardata.level == chardata.level:
                    chardata.earnedxp = chardata.xp-last.chardata.xp
                else:
                    chardata.earnedxp = ledata.levelxp[last.chardata.level]-last.chardata.xp+chardata.xp
            return chardata
        except Exception as e:        
            raise FileClashException(f"Failed to read saveslot {slot}")

    # Handle zone change calculations
    lastzone = LastCheck()
    def newzone(self,zones):
        try:
            timenow = datetime.now()
            chardata = self.checkchar(self.lastzone,self.lastsslot,timenow)
            if self.lastzone.time != 0 and chardata.playtime > 0:
                xppm = int(chardata.earnedxp/chardata.playtime*60)
                lp = chardata.xp/(ledata.levelxp[chardata.level]/100)
                pl = chardata.earnedxp/chardata.playtime*60*60/ledata.levelxp[chardata.level]
                ts = ""
                for tlid in chardata.stabDB:
                    if tlid in self.lastzone.chardata.stabDB and self.lastzone.chardata.stabDB[tlid] != chardata.stabDB[tlid]:
                        ts = f" - Timeline: {tlid} Stability change from {self.lastzone.chardata.stabDB[tlid]} to {chardata.stabDB[tlid]}"
                self.addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {chardata.charname}({chardata.level}+{lp:.1f}%) - {zones[0]:12} - {chardata.earnedxp}xp in {chardata.playtime}secs = {xppm}xp/min {pl:.1f}lvl/hr {ts}",True)
            self.lastzone.update(timenow,chardata)
        except FileClashException as e:
            pass # trying to read file whilst game is writing it

    # Monitor ongoing XP gains
    lastchar = LastCheck()
    played = CharPlayed()
    def newsave(self,sslot):
        try:
            timenow = datetime.now()
            chardata = self.checkchar(self.lastchar,sslot,timenow)
            if chardata.earnedxp > 0:
                if self.lastchar.chardata.charname != chardata.charname:
                    self.played = CharPlayed()
                else:
                    if chardata.earnedxp > 0:
                        self.played.update(chardata)
                        self.addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {chardata.charname}({chardata.level}+{self.played.perclevel:.1f}%) - {self.played.xpperhour:8.0f}xp/hr {self.played.levelperhour:.1f}lvl/hr",False)
            self.lastchar.update(timenow,chardata)
        except FileClashException as e:
            pass # trying to read file whilst game is writing it

    # Monitor Player Log 
    @utils.background
    def watchlog(self):
        firstime = True
        sline = 0
        logfile = "testlog.txt"
        if not os.path.exists(logfile): # testlog.txt used for debugging
            logfile = settings.get("ledir") + "Player.log"
        while self.watching:
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
                    f.close()                
            except Exception as e:
                print("Error in watchlog",e,type(e))
            time.sleep(settings.get("zonedelay"))

    #Monitor Saveslot
    @utils.background
    def watchsave(self):
        lastupd = 0
        while self.watching:
            if self.lastsslot != "0":
                upd = os.stat(ledata.filenameforslot(settings.get("ledir"),self.lastsslot)).st_mtime
                if upd != lastupd:
                    utils.runcb("save",self.lastsslot)
                lastupd = upd            
        time.sleep(settings.get("savedelay"))

    def run(self):
        # find last saved slot
        if self.lastsslot != None: # at least 1 save file found
            # assign callbacks 
            utils.addcb("zone",self.newzone)
            utils.addcb("save",self.newsave)
            utils.addcb("log",self.checkzonechange)

            # run once to setup a 'before'
            self.newzone([]) 

            # start monitors
            self.watchlog() 
            self.watchsave()

            # Main loop...
            print("Last Epoch Watcher Active")
            while self.watching:
                time.sleep(settings.get("quitdelay"))
            print("Last Epoch Watcher Ending...")
        
        else:
            print("No Last Epoch save files found - check settings.json for correct path")

LEWatch().run()