## LEXPWatch - XP monitoring for Last Epoch ##

This is VERY much work-in-progress - sharing for feedback/ideas!

### What it Does ###
It monitors your Player.log/save slots and reports how much XP you're earning when playing and specifically in each 'area' you enter/leave

### How it does it ###
Python Code - I've tried to avoid using external dependencies - I think it should 'just work'

It monitors "Player.log" which is updated each time you change zone - the zone names are internal mapnames but it's easy to see what they mean.

It also monitors your more recently updated Saveslot file (last character played?) to see if you've gained XP or Levels
|
### How to Use ###
Clone the repo and run lewatch.py - it runs forever, Ctrl-Break to halt it.

Output goes to console - redirect it to a file if you'd prefer!

I've included the path for Linux installs but I don't have a way to test that so feedback apprec on that too!

### Options ###
The first run will create 'settings.json' - that contains a few options
*ledir - the path to your Last Epoch save folder (Player.log file stored in there)
*zonedelay - how often to check for zone changes
*savedelay - how often to check your savefile 
*quitdelay - how often to check to see if the program ended (not currently implemented!)

'delays' should always be at least 1 (they're in seconds) - anything lower will waste CPU doing nothing...

### It's not working/I'd like different stats/Help! ###

Fire an Issue and I'll try to help!