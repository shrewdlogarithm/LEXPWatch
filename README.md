## LEXPWatch - Progress monitoring for Last Epoch ##

This is VERY much work-in-progress - sharing for feedback/ideas!

### What does it do? ###
It monitors how much XP you're earning over time and per-zone - it  also reports Stability gains from Monolith Echoes

### Sample Output ###
Zone-Change

`2022-08-02 13:02:45 - MrsStabby(80+35.9%) - M_M150       - 156004xp in 120secs = 78002xp/min 2.6lvl/hr  - Timeline: 9 Stability change from [233] to [266]`

Character "MrsStabby" Level 80 and 35.9% of the way to 81 earned 156004 XP in 120 seconds in area 'M_M150' (a Monolith Echo)
XP/min and lvl/hr are calculated 
Timeline Stability change is also reported

Ongoing XP earned (updated "live" as you're playing)

`MrsStabby(80+35.9%) -  5400138xp/hr 3.0lvl/hr`

*Note: This counts time spent in areas where you earned XP - it ignores time spent in hubs where no XP was earned*

### How do I run it? ###
You'll need Python (3.6 or higher) installed - Linux normally has it, it's pretty easy to install in Windows these days too!

Clone or download this repository (you only need the 3 .py files) and run "python lewatch.py"

Output goes to the console but also saved to "slot?.log" for each saveslot which has been monitored

### How does it work? ###
It monitors the "Player.log" file which is updated each time you change zone 

It also monitors your saveslot files to see if you've gained XP or Levels

### Options ###
First time you run it, it creates a file 'settings.json' which contains the default options

* ledir - the path to your Last Epoch save folder (Player.log file stored in there) - if it's not working, check this is correct!!
* zonedelay - how often to check for zone changes
* savedelay - how often to check your savefile 
* quitdelay - how often to check to see if the program ended (not currently implemented!)

Delay numbers should always be at least 1 (they're in seconds) - anything lower will thrash your CPU for no good reason...

### It's not working/I'd like different stats/Help! ###

Feel-free to raise Issues with ideas or suggestions and I'll try to help

Thanks for reading this far!
