from config import *
import logging
import inspect
import time
import copy
import random
from Commands import *

class Game():
		
	""" Default Game Settings for every Server """
	
	data = {} #all the game data
	
	data["server"] = ""
	data["id"] = ""
	data["gm"] = ""
	data["name"] = ""
	data["session"] = ""
	data["description"] = ""
	data["datetime"] = ""
	data["timezone"] = ""
	data["minplayers"] = "3"
	data["maxplayers"] = "7"
	data["sidelineson"] = "1"
	data["minsidelines"] = "0" #int
	data["maxsidelines"] = data["maxplayers"]
	data["textchannel"] = ""
	data["voicechannel"] = ""
	data["image"] = ""
	data["roster"] = [] # tuples of (id, "fixed"/"unfixed")
	data["sideline"] = []
	data["gpreward"] = ""
	data["xpreward"] = "" # string
	data["priorityamt"] = "1"
	data["duration"] = ""
	data["minlevel"] = ""
	data["maxlevel"] = ""
	data["tier"] = "1"
	#data["linkchronus"] = ""
	data["link"] = ""

	# Finishing
	data["completed"] 			= "0" #Bool
	data["published"] 			= "0" #Bool
	data["publishid"] 			= [] # id for the message that holds the published game data embed. Tuple of (id, channel.id)
	data["publishchannels"] 	= [] #channel/s the game will be published to and unpublished from
	data["completedchannels"] 	= [] #channel/s the game will be published to and unpublished from
	
	# Reminder
	data["reminderson"] = "0" #Bool
	data["remindwhen"] = "60" #minutes before the game, min rsvptime (if on), max 24 hours
	data["remindermsg"] = "" # What's said
	data["reminders"] = AutoVivification()
	
	# Update Whispers
	data["whispergmdetailupdates"] = "0" #Bool 		Whether to whisper detail changes to the game to the GM
	data["whispergmrosterupdates"] = "0" #Bool 		Whether to whisper roster changes to the game to the GM
	data["whispergmsidelineupdates"] = "0" #Bool 		Whether to whisper sideline changes to the game to the GM
	data["whisperplayersdetailupdates"] = "0" #Bool 	Whether to whisper players on the roster of changes to the game details
	data["whisperplayersrosterupdates"] = "0" #Bool 	Whether to whisper players on the roster of changes to the game roster
	data["whispersidelinedetailupdates"] = "0" #Bool 	Whether to whisper players on the sideline of changes to the game details
	data["whispersidelinerosterupdates"] = "0" #Bool 	Whether to whisper players on the sideline of changes to the game roster

	# Roster lockout
	data["rosterlockon"] 			= "0" #Bool 	Whether the roster with lock at the designated time
	data["rosterlockbeforestart"] 	= "0" #Int 		How many minutes before game start (positive for before, negative for after) that roster locks for players
	data["onlygmadd"] 				= "0" #Bool 	Whether only the GM can add players, even preventing Promote from Sidelines
	
	def __init__(self, serverdict, discordserverid, datetime, timezone, makerid, gameid, copyid="default", tabs=0):
		""" Sets the default data for every server when the bot joins """	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Initialising game object")
		tabs += 1
		
		# Copy the default data
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " deep copy of gameid " + copyid)
		self.data = copy.deepcopy(serverdict["games"][copyid])
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting unique data")
		self.data["server"] 	= discordserverid
		self.data["id"] 		= gameid
		self.data["gm"] 		= makerid
		self.data["datetime"] 	= datetime
		self.data["timezone"]	= timezone
		
		if copyid != "default":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Blanking copied data")
			# A game was copied from an existing one
			# Need to clear some data
			self.data["roster"] 		= copy.deepcopy(serverdict["games"]["default"]["roster"])
			self.data["sideline"] 		= copy.deepcopy(serverdict["games"]["default"]["sideline"])
			self.data["completed"] 		= copy.deepcopy(serverdict["games"]["default"]["completed"])
			self.data["published"] 		= copy.deepcopy(serverdict["games"]["default"]["published"])
			self.data["publishid"] 		= copy.deepcopy(serverdict["games"]["default"]["publishid"])
			self.data["reminders"] 		= copy.deepcopy(serverdict["games"]["default"]["reminders"])
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Game.__init__")
		logger.debug(tb(tabs) + str(self))



		
