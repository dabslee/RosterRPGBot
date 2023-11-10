from config import *
import inspect
import logging
import time
from Functions import *

""" Stores all the commands and the functions they call """

SS = AutoVivification() # Server Setting: Variables that will be stored per command
AC = AutoVivification() # All commands

AC["function"]	= BotInfoBox # returns an info box about the bot
AC["gameid"]    = AutoVivification() # Needs to be here before AC["gameid"]["function"] is set, or otherwise it gets wiped
# ~~~~~~~~~~~~~~~~~~~~~~~~ Server Owner Command Functions

# ~~~ Server Settings

# Functions
AC["settings"]["function"] 	= GSSettings # Has to have the "function" dictionary item or it replaces all the other AC settings functions below
AC["setting"]				= GSSettings # Alias
AC["newgame"] 				= MakeNewGame #Give UTCtime create a game for that date and time. Otherwise, returns the guide for making a newgame.
AC["copy"] 					= GameCopy 
AC["priority"]  			= GetPriority
AC["prio"]  				= GetPriority# Alias
AC["p"]  					= GetPriority# Alias
AC["alltimezones"] 			= PrintTimezones
AC["timezones"]				= PrintTimezones # Alias
AC["games"] 				= GetGames
AC["g"] 					= GetGames # Alias
AC["gameid"]["function"]	= GSGameData # async function
AC["mytimezone"] 			= GSMyTimezone
AC["mytz"] 					= GSMyTimezone # Alias
AC["tz"] 					= GSMyTimezone # Alias
AC["resetpriorities"]		= ResetPriorities
AC["listme"] 				= ListMe		# using ListPlayer, and listme authority	
AC["rosterme"] 				= ListMe		# using ListPlayer, and rosterme authority		
AC["sidelineme"] 			= ListMe		# using ListPlayer, and sidelineme authority		
AC["unlistme"] 				= UnlistMe		# using UnlistPlayer, no authority req
AC["unrosterme"] 			= UnlistMe		# using UnlistPlayer, no authority req
AC["unsidelineme"] 			= UnlistMe		# using UnlistPlayer, no authority req

# Static Authority Commands
SS["settings"]["authority"]["settings"] 		= "1" # Who can view and change roster bot settings
SS["settings"]["authority"]["default"] 			= "1" # Who can view and change the default data for new games
SS["settings"]["authority"]["prioritieson"] 	= "1" # Who can decide if the priority system is on or not.
SS["settings"]["authority"]["levelcapson"] 		= "1" # Who can decide if the priority system is on or not.
SS["settings"]["authority"]["resetpriorities"] 	= "1" # Who can reset the priorities for all players
SS["settings"]["authority"]["editcompleted"] 	= "1" # Who can edit games that are marked complete
SS["settings"]["authority"]["uncomplete"] 		= "1" # Who can mark a game as not completed
SS["settings"]["authority"]["rosterfixed"]		= "1" # Who can add themselves/others in fixed position in rosters
SS["settings"]["authority"]["changepriority"] 	= "1" # Who can change the priority amount of games
SS["settings"]["authority"]["newgame"] 			= "2" # Who can create new games
SS["settings"]["authority"]["gameid"] 			= "2" # Who can view and change game data. May vary depending on whether GMs can edit other GM's games, and may allow 3s if only viewing game data
SS["settings"]["authority"]["list"] 			= "2" # Who can list and unlist any player for a given game
SS["settings"]["authority"]["roster"] 			= "2" # Who can roster and unroster any player for a given game (won't add to sidelines)
SS["settings"]["authority"]["sideline"]			= "2" # Who can sideline and unsideline any player for a given game (won't add to roster)
SS["settings"]["authority"]["copy"]				= "2" # Who can copy existing games as a newgame
SS["settings"]["authority"]["viewpriorities"] 	= "3" # Who can view any player priority levels
SS["settings"]["authority"]["viewallgames"] 	= "3" # Who can see upcoming games
SS["settings"]["authority"]["viewgame"] 		= "3" # Who can view game data
SS["settings"]["authority"]["listme"] 			= "3" # Who can list and unlist themselves for a given game
SS["settings"]["authority"]["rosterme"] 		= "3" # Who can roster and unroster themselves for a given game (won't add to sidelines)
SS["settings"]["authority"]["sidelineme"]		= "3" # Who can sideline and unsideline themselves for a given game (won't add to roster)
SS["settings"]["authority"]["mytimezone"]		= "3" # Who can get or set their own timezone
SS["settings"]["authority"]["sidelinefixed"]	= "3" # Who can add themselves/people in fixed position in sidelines
AC["settings"]["authority"]						= GSAuthority

# Authority 1 commands
# Server Roles per Authority Level
SS["settings"]["roles"]["1"]	= [] # role id string. What guild roles other than server owner can change the bot's settings. If blank then only the Guild Owner
SS["settings"]["roles"]["2"]	= [] # role id string. What guild roles can create and edit games. If blank then anyone.
SS["settings"]["roles"]["3"]	= [] # role id string. What guild roles for everyone else. Some server owners may want this to be GMs only. If blank then anyone.
SS["settings"]["roles"]["4"]	= [] # role id string. These guild roles explicitly have no access to rosterbot functions. Easier to use than listing all guild roles in 3 but with one or more left out
AC["settings"]["roles"] 		= GSRoles

# # ~~~ Discord Channel Settings
SS["settings"]["botannouncechannel"]  	= [] # "sets the discord server channel for the bot to make announcements to
AC["settings"]["botannouncechannel"] 	= GSBotannouncechannel

SS["settings"]["connectionmsgid"]  		= [] # (Message ID, Channel ID) for messages reporting the bot's current status for this GUILD

# ~~~ Automatic Priority Reset
SS["settings"]["nextpriorityreset"]  	= "" # UTC datetime string of when next priority reset occurs. Won't store the timezone, it will always be UTC
SS["settings"]["priorityresetfreq"]  	= "0" # How often priority gets automatically reset, in Days. 0 means never
SS["settings"]["priorityresetmsg"]		= "ATTENTION: All player priorities have been reset to 0!" # What is said in the priority reset message, if anything
#SS["settings"]["lastpriorityresetid"]	= "" # message id for the last priority reset, to be deleted on autopriorityreset
AC["settings"]["nextpriorityreset"] 	= GSNextPriorityReset
AC["settings"]["priorityresetfreq"] 	= GSPriorityResetFreq
AC["settings"]["priorityresetmsg"] 		= GSPriorityResetMsg

# ~~~ Per-Game Settings

# # playermaxconsecutive - return str and functions

SS["settings"]["playermaxconsecutive"]  = "-1" # returns how many games a player can play immediately after finishing a game
AC["settings"]["playermaxconsecutive"] 	= GSPlayerMaxConsecutive

# # playermaxroster - return str and functions
SS["settings"]["playermaxroster"]  	= "1" # returns how many future games a player can be rostered for at a time. -1 means no limit
AC["settings"]["playermaxroster"] 	= GSPlayerMax

# playermaxsideline - return str and functions
SS["settings"]["playermaxsideline"] = "1" # returns how many future games a player can be sidelined for at a time. -1 means no limit
AC["settings"]["playermaxsideline"] = GSPlayerMax

# gmseditown
SS["settings"]["gmsonlyeditown"] = "0" # whether GMs only edit their own games or if anyone with edit permission can edit any
AC["settings"]["gmsonlyeditown"] = GSGMsOnlyEditOwn

# prioritieson
SS["settings"]["prioritieson"] = "1" # whether the program even uses priorities, or just takes players in order of listing
AC["settings"]["prioritieson"] = GSPrioritiesOn

# levelcapson
SS["settings"]["levelcapson"] = "1" # whether the program even uses priorities, or just takes players in order of listing
AC["settings"]["levelcapson"] = GSLevelCapsOn

#~~~~~~~~~~~~~~~~~~~~~~~~ Commands for GMs to make and edit games

# Modify Game Commands

# Ensure there's a key and generic functions for every game, in case I miss one
for each in Game.data.keys():
	AC["gameid"][each] 		= GenericSetting

AC["gameid"]["update"] 		= GameUpdateEmbeds
AC["gameid"]["audit"] 		= GameAudit

# ~~~ Requires Discord IDs
AC["gameid"]["server"] 			= GSserver
AC["gameid"]["gm"] 				= GSgm
AC["gameid"]["textchannel"] 	= GStextchannel
AC["gameid"]["text"] 			= GStextchannel		#aliases
AC["gameid"]["tc"] 				= GStextchannel		#aliases
AC["gameid"]["voicechannel"] 	= GSvoicechannel
AC["gameid"]["voice"] 			= GSvoicechannel	#aliases
AC["gameid"]["vc"] 				= GSvoicechannel	#aliases
AC["gameid"]["link"] 			= GSlink
AC["gameid"]["image"] 			= GSimage
AC["gameid"]["roster"] 			= GSroster			# Calls list (below)
AC["gameid"]["sideline"] 		= GSsideline		# Calls list (below)
AC["gameid"]["list"] 			= AddToTeam			# Adding others using ListPlayer and list, roster or sideline authority
AC["gameid"]["unlist"] 			= Sunlist			# Removing others using UnlistPlayer
AC["gameid"]["unroster"] 		= Sunlist			# Removing others using UnlistPlayer	
AC["gameid"]["unsideline"] 		= Sunlist			# Removing others using UnlistPlayer

# ~~~ Strings
AC["gameid"]["name"] 			= GSname
AC["gameid"]["session"] 		= GSsession
AC["gameid"]["description"] 	= GSdescription
AC["gameid"]["gpreward"] 		= GSgpreward
AC["gameid"]["xpreward"] 		= GSxpreward
AC["gameid"]["duration"] 		= GSduration
AC["gameid"]["tier"] 			= GStier

# ~~~ Requires Time Conversions
AC["gameid"]["datetime"] 		= GSdatetime
AC["gameid"]["date"] 			= GSdatetime
AC["gameid"]["time"] 			= GSdatetime
AC["gameid"]["timezone"] 		= GStimezone

# ~~~ Ints
AC["gameid"]["minplayers"] 		= GSminplayers
AC["gameid"]["maxplayers"] 		= GSmaxplayers
AC["gameid"]["maxsidelines"] 	= GSmaxsidelines
AC["gameid"]["minlevel"] 		= GSminlevel
AC["gameid"]["maxlevel"] 		= GSmaxlevel
AC["gameid"]["priorityamt"] 	= GSpriorityamt

# ~~~ Toggles On/Off
AC["gameid"]["sidelineson"] 					= GSsidelineson
AC["gameid"]["whispergmdetailupdates"] 			= GSwhisperupdates
AC["gameid"]["whisperplayersdetailupdates"] 	= GSwhisperupdates
AC["gameid"]["whispersidelinedetailupdates"]	= GSwhisperupdates
AC["gameid"]["whispergmrosterupdates"] 			= GSwhisperupdates
AC["gameid"]["whisperplayersrosterupdates"] 	= GSwhisperupdates
AC["gameid"]["whispersidelinerosterupdates"] 	= GSwhisperupdates
AC["gameid"]["whispergmsidelineupdates"] 		= GSwhisperupdates

AC["gameid"]["completed"] 			= GScompleted
AC["gameid"]["complete"] 			= GScompleted #alias
AC["gameid"]["published"] 			= GSpublish
AC["gameid"]["publish"] 			= GSpublish #alias
AC["gameid"]["publishchannels"] 	= GSpublishchannels #alias
AC["gameid"]["completedchannels"]	= GSpublishchannels #alias

# ~~~ Reminders
AC["gameid"]["reminderson"]		= GSreminderson
AC["gameid"]["remindwhen"] 		= GSremindwhen
AC["gameid"]["remindermsg"] 	= GSremindermsg
AC["gameid"]["reminders"] 		= Greminders
AC["gameid"]["sendmsg"] 		= SendMessage
AC["gameid"]["msg"] 			= SendMessage
AC["gameid"]["message"] 		= SendMessage
AC["gameid"]["msgall"] 			= SendMessage
AC["gameid"]["msgroster"] 		= SendMessage
AC["gameid"]["msgrosters"] 		= SendMessage
AC["gameid"]["msgsidelines"]	= SendMessage
AC["gameid"]["msgsideline"] 	= SendMessage

# ~~~ RosterLock
AC["gameid"]["rosterlockon"] 			= GSrosterlockon
AC["gameid"]["rosterlockbeforestart"] 	= GSrosterlockbeforestart
AC["gameid"]["onlygmadd"]	 			= GSonlygmadd


