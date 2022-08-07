# Converted to OO and NOT YET FULLY TESTED

import time,os,glob,re,utils
from datetime import datetime
from lefuncs import levelxp

class FileClashException(Exception):
    def __init__(self, message='Key Empty'):
        super(FileClashException, self).__init__(message)

class LEWatch:
    def __init__(self):
        self.watching=True

        self.path = os.getenv("USERPROFILE") # should be the Windows AND Linux base path - Linux untested tho...
        if self.path: # we're on Windows
            self.path = self.path + "/appdata/locallow/"
        else: # almost certainly Linux as LE doesn't run on OSX??
            self.path = os.getenv("HOME") + "/.config/unity3d/" # this is untested as yet - I'm guessing at the Linux path here...
        
        # Default Settings
        self.settings = {
            "ledir": self.path + "/Eleventh Hour Games/Last Epoch/",
            "zonedelay": 5,
            "savedelay": 5,
            "quitdelay": 5
        }              

    # Output to file/console
    overprint = False    
    def addlog(self,log,term):
        if term:
            if self.overprint:
                print("")
                self.overprint = False
            endc = "\n"
        else:
            endc = "\r"
            self.overprint = True
        print(log,sep="",end=endc)
        try:
            with open(f"slot{self.lastsslot[0]}.log","a") as lf:
                lf.write(log + "\n")
        except Exception as e:
            pass # may be read-only filesystem - no matter...

    # Find last played character slot
    lastsslot = ["0",0]
    def findlastsslot(self): 
        mrecent = 0
        mrfile = "0"
        slotfiles = glob.glob(self.settings["ledir"] + "Saves/1*")
        for slotfile in slotfiles:
            mtime = os.path.getmtime(slotfile)
            if mtime > mrecent:
                mrecent = mtime
                mrfile = slotfile    
        if mrfile != "0":
            self.lastsslot = [re.findall(r'\d+', mrfile)[-1],mrecent]
        else:
            print("Cannot find any character saves - check path in settings.json")
            self.watching = False    

    # Return saveslot file (testchar.txt used for testing without the game running/installed)
    def filenameforslot(self,sslot):
        if os.path.exists("testchar.txt"):
            return "testchar.txt"
        else:
            return self.settings["ledir"] + "/Saves/1CHARACTERSLOT_BETA_" + sslot    

    # Load character data from savefile for slot
    def getchardb(self,sslot):
        try:
            return utils.loadjson(self.filenameforslot(sslot),5)
        except Exception as e:        
            raise FileClashException(f"Failed to read saveslot {sslot}")

    # Handle zone changes
    lastzonename = "Unknown"
    def checkzonechange(self,l):
        zc = re.match(r'Loading Scene(.*)', l)
        if zc:
            zones = [self.lastzonename,zc.group(1).strip()]
            self.lastzonename = zc.group(1).strip()
            self.findlastsslot()
            utils.runcb("zone",zones)

    # Handle ongolng XP calculation
    def checkchar(self,last,slot,timenow):
        chardb = self.getchardb(slot)
        currcharname = chardb["characterName"]
        level = int(chardb["level"])
        charxp = int(chardb["currentExp"])
        intvl = 0
        totalxp = 0
        mrundb={}
        for run in chardb["monolithRuns"]:
            mrundb[run["timelineID"]] = [run["stability"]]
        if last[0] != 0:
            intvl = int((timenow-last[0]).total_seconds())
            if last[1] == level:
                totalxp = charxp-last[2]
            else:
                totalxp = levelxp[last[1]]-last[2]+charxp
        return currcharname,level,charxp,intvl,totalxp,mrundb

    # Handle zone change calculations
    lastzone = [0,0,0]
    laststab = {}
    def newzone(self,zones):
        try:
            timenow = datetime.now()
            currcharname,level,charxp,intvl,totalxp,mrundb = self.checkchar(self.lastzone,self.lastsslot[0],timenow)
            if self.lastzone[0] != 0 and intvl > 0:
                xppm = int(totalxp/intvl*60)
                lp = charxp/(levelxp[level]/100)
                pl = totalxp/intvl*60*60/levelxp[level]
                ts = ""
                for tlid in mrundb:
                    if tlid in self.laststab and self.laststab[tlid] != mrundb[tlid]:
                        ts = f" - Timeline: {tlid} Stability change from {self.laststab[tlid]} to {mrundb[tlid]}"
                self.addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {currcharname}({level}+{lp:.1f}%) - {zones[0]:12} - {totalxp}xp in {intvl}secs = {xppm}xp/min {pl:.1f}lvl/hr {ts}",True)
                self.laststab = mrundb
            self.lastzone=[timenow,level,charxp]
        except FileClashException as e:
            pass # trying to read file whilst game is writing it

    # Monitor ongoing XP gains
    ccxp=0
    ccplaytime=0
    lastchar = [0,0,0,""]
    def newsave(self,sslot):
        try:
            timenow = datetime.now()
            currcharname,level,charxp,intvl,totalxp,mrundb = self.checkchar(self.lastchar,sslot,timenow)
            if totalxp > 0:
                if self.lastchar[3] != currcharname:
                    self.ccxp=0
                    self.ccplaytime=0
                else:
                    if totalxp > 0:
                        self.ccxp += totalxp
                        self.ccplaytime += intvl
                        lp = charxp/(levelxp[level]/100)
                        ph = (self.ccxp/self.ccplaytime*60*60)
                        pl = ph/levelxp[level]
                        self.addlog(f"{timenow:%Y-%m-%d %H:%M:%S} - {currcharname}({level}+{lp:.1f}%) - {ph:8.0f}xp/hr {pl:.1f}lvl/hr",False)
            self.lastchar = [timenow,level,charxp,currcharname]
        except FileClashException as e:
            pass # trying to read file whilst game is writing it

    # Monitor Player Log 
    @utils.background
    def watchlog(self):
        firstime = True
        sline = 0
        logfile = "testlog.txt"
        if not os.path.exists(logfile): # testlog.txt used for debugging
            logfile = self.settings["ledir"] + "Player.log"
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
            time.sleep(self.settings["zonedelay"])

    #Monitor Saveslot
    @utils.background
    def watchsave(self):
        lastupd = 0
        while self.watching:
            if self.lastsslot[0] != "0":
                upd = os.stat(self.filenameforslot(self.lastsslot[0])).st_mtime
                if upd != lastupd:
                    utils.runcb("save",self.lastsslot[0])
                lastupd = upd            
        time.sleep(self.settings["savedelay"])

    def run(self):
        # load/save settings
        self.settings = {**self.settings,**utils.loadjson("settings.json")}
        utils.savejson("settings.json",self.settings)

        # find last saved slot
        self.findlastsslot()        
        
        # assign callbacks 
        utils.addcb("zone",self.newzone)
        utils.addcb("save",self.newsave)
        utils.addcb("log",self.checkzonechange)

        # run once to setup a 'before'
        self.newzone([]) 

        # start monitors
        self.watchlog() 
        self.watchsave()

        print("Last Epoch Watcher Active")

        # Loop quietly...
        while self.watching:
            time.sleep(self.settings["quitdelay"])
        print("Last Epoch Watcher Ending...")

LEWatch().run()