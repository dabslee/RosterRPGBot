from config import *
import inspect
import logging
import asyncio
import time
import json
import copy
import Commands
import GameData
import os
import collections.abc
from pathlib import Path
from discord.ext.commands import Bot
from discord import Game, Status
from InternalFuncs import deepupdate


# Initialise the Discord Servers directory and files
# Get the directory of this file
DserverFilepath = Path(__file__).parent


# Check if a Discord Servers directory exists and make it if not
DserverFilepath = DserverFilepath.joinpath("Dservers")
#print(DserverFilepath)
try:
	if not DserverFilepath.exists():
		Path.mkdir(DserverFilepath)
except OSError as e:
	edata = PrintException()
	print("error in Dserver.py: " + edata)
	logger.error(edata)

# Get list of existing Dserver files
files = [e for e in DserverFilepath.iterdir() if e.is_file() and  e.suffix == ".txt" and "dserver" in str(e.name).lower()]

import collections.abc

lastdata = {}

class Dserver():
	
	AllDservers = {}
		
	def ReadInDservers(self, tabs=0):
		""" Reads the Server text files and converts them to Server objects """		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ReadInDservers")
		tabs += 1
	
		for each in files:
			logger.debug(tb(tabs) + str(each.name))
			with open(each, "r") as f:
				data 								 = json.loads(f.readline())
				Dserver.AllDservers[data["GuildID"]] = copy.deepcopy(Commands.SS)  # Copy default Server settings in case I've added new ones
				deepupdate(Dserver.AllDservers[data["GuildID"]], data) # overwrite default data with file data
				
				# make sure game data has all current key value pairs
				for each in Dserver.AllDservers[data["GuildID"]]["games"].keys():
					Dserver.AllDservers[data["GuildID"]]["games"][each] = copy.deepcopy(GameData.Game.data)
					deepupdate(Dserver.AllDservers[data["GuildID"]]["games"][each], data["games"][each]) # overwrite default data with file data
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " data after deepcopy and deepupdate clean:")
				deeplogdict(Dserver.AllDservers[data["GuildID"]], "debug", tabs+1)
				logger.debug("") # blank line
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " lastdata print out")
				if int(data["GuildID"]) not in lastdata.keys():
					# create the first record
					logger.debug(tb(tabs+1) + "Creating a lastdata record")
					lastdata[int(data["GuildID"])] = str(Dserver.AllDservers[int(data["GuildID"])])
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Filtering ActiveGames")
				Dserver.AllDservers[data["GuildID"]]["activegames"] = []
				for gameid, gdata in Dserver.AllDservers[data["GuildID"]]["games"].items():
					logger.debug(tb(tabs+1) + "Checking gameid " + gameid)
					if gdata["completed"] == "0" and gdata["published"] == "1":
						logger.debug(tb(tabs+2) + "Adding " + gameid)
						Dserver.AllDservers[data["GuildID"]]["activegames"].append(gameid)
					else:
						logger.debug(tb(tabs+2) + "Not adding to activegames")
						
					if "completedchannels" not in gdata.keys(): # Add new variable
						gdata["completedchannels"] = copy.deepcopy(Dserver.AllDservers[data["GuildID"]]["games"]["default"]["completedchannels"])
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ActiveGames: #" + str(len(Dserver.AllDservers[data["GuildID"]]["activegames"])) + " " + str(Dserver.AllDservers[data["GuildID"]]["activegames"]))
				
				# Variable renames
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking variable name changes")
				if "priority" in Dserver.AllDservers[data["GuildID"]]["settings"]["authority"].values():
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Changing settings authority priority to settings authority viewpriorities")
					Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["viewpriorities"] = Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["priority"]
					del Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["priority"]

				if "games" in Dserver.AllDservers[data["GuildID"]]["settings"]["authority"].values():
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Changing settings authority games to settings authority viewallgames")
					Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["viewallgames"] = Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["games"]
					del Dserver.AllDservers[data["GuildID"]]["settings"]["authority"]["games"]
					
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ReadInDservers")
	
	def CheckInvitedServers(self, thisbot, tabs=0):	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CheckInvitedServers")
		tabs += 1
		
		for G in thisbot.guilds:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking G: " + str(G))
			tabs += 1
			if G.id in Dserver.AllDservers: # Server file exists. Update guild owner and players and be done
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild " + str(G.id) + " " + str(G.name) + " exists.")
				tabs += 1
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild owner: " + str(G.owner))
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild owner_id: " + str(G.owner_id))
				Dserver.AllDservers[G.id]["GuildOwnerID"]  = G.owner_id
				
				# Copy or Update all the player ids
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking Players")
				for p in G.members:
					#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking P: " + str(p))
					if str(p.id) not in Dserver.AllDservers[G.id]["players"]:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Initialising new player data for " + str(p.id) + " " + str(p.nick))
						playerdata 	= {"p":[], "r": [], "gp":[], "gr":[], "s":[], "l":[], "tz":""} #played, rostered, gamemaster played, gamemaster rostered, sidelined, last games from previous week, my timezone
						Dserver.AllDservers[G.id]["players"][str(p.id)] = copy.deepcopy(playerdata)				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking  for New Players Complete")
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking  for Players that left")
				guildpids = [str(p.id) for p in G.members if str(p.id) not in Dserver.AllDservers[G.id]["players"]]
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " left players are: " + str(guildpids))
				for p in guildpids:
					logger.debug(tb(tabs+1) + "Clearing game data (if any) for " + p + ": " + str(Dserver.AllDservers[G.id]["players"][p].items()))
					pdata = Dserver.AllDservers[G.id]["players"][p]
					listings = [pdata["r"], pdata["s"], pdata["p"], pdata["gp"], pdata["gr"]]
					listname = ["roster", "sideline", "roster", "gm", "gm"]
					logger.debug(tb(tabs+1) + "listings: " + str(listings))
					for num, listing in enumerate(listings):
						thislist = listname[num]
						logger.debug(tb(tabs+2) + "this " + thislist + ": " + str(listing.items()))
						for game in listings:
							logger.debug(tb(tabs+3) + "game: " + game)
							gdata = Dserver.AllDservers[G.id]["games"][game]
							if num > 2:
								logger.debug(tb(tabs+3) + "Removing game mastered data")
								gdata["gm"] = p + " (left)"
							else:
								logger.debug(tb(tabs+2) + "Removing player data")
								for pos, (rp, status) in enumerate(gdata[thislist]):
									if rp == p:
										logger.debug(tb(tabs+3) + "removing from pos " + str(pos))
										gdata[thislist][pos][0] == p + " (left)"
							logger.debug(tb(tabs+3) + "End of game check")
						logger.debug(tb(tabs+2) + "End of listing check")				
					logger.debug(tb(tabs+2) + "Removing from guild data")
					del Dserver.AllDservers[G.id]["players"][p]					
					logger.debug(tb(tabs+1) + "End of player check")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of removing players that left")
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " lastdata print out")
				if G.id not in lastdata.keys():
					# create the first record
					logger.debug(tb(tabs+1) + "Creating a lastdata record")
					lastdata[G.id] = str(Dserver.AllDservers[G.id])
				elif lastdata[G.id] != str(Dserver.AllDservers[G.id]):					
					logger.debug(tb(tabs+1) + "Updating last data for this Server:")
					deeplogdict(Dserver.AllDservers[G.id], "debug", tabs+1)
					logger.debug("") # blank line
					lastdata[G.id] = str(Dserver.AllDservers[G.id])
				else:
					logger.debug(tb(tabs+1) + "Current data and last data match")
			else: # Create a new guild
				#Update the Server data
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating Guild data: " + str(G))
				data 					  = {}
				data["GuildID"] 		  = G.id
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild.id: " + str(G.id))
				data["GuildOwnerID"] 	  = G.owner.id
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild.owner.id: " + str(G.owner.id))
				data["GuildName"]		  = G.name
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild.name: " + G.name)
				data["GuildFileName"] 	  = "Dserver " + str(G.id) + ".txt"
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " GuildFileName: " + data["GuildFileName"])
				data["BotActive"]		  = True
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Initialising players")
				playerdata 				  = {"p":[], "r": [], "gp":[], "gr":[], "s":[], "l":[], "tz":""} #played, rostered, gamemaster played, gamemaster rostered, sidelined, last games from previous week
				data["players"]			  = {}
				for m in G.members:
					data["players"][str(m.id)] = copy.deepcopy(playerdata) # have to turn id into string because json.dump does this when writing file out https://stackoverflow.com/questions/1450957/pythons-json-module-converts-int-dictionary-keys-to-strings			
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Initialising games and default game")
				data["games"] 			  = {}
				data["games"]["default"]  = copy.deepcopy(GameData.Game.data)				
				
				# Other Guild Variables (add new variables here)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Initialising other variables")
				data["activegames"] = []
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Copying to AllDservers")			
				thisServer 		  			= copy.deepcopy(data)
				Dserver.AllDservers[G.id] 	= thisServer
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Copying default server settings")
				thisServer.update(copy.deepcopy(Commands.SS)) # Copy default Server settings in case I've added new ones
				
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " lastdata print out")
				if G.id not in lastdata.keys():
					# create the first record
					logger.debug(tb(tabs+1) + "Creating a lastdata record")
					lastdata[G.id] = str(Dserver.AllDservers[G.id])
				elif lastdata[G.id] != str(Dserver.AllDservers[G.id]):					
					logger.debug(tb(tabs+1)+ "thisServer:")
					deeplogdict(Dserver.AllDservers[G.id], "debug", tabs+2)
					logger.debug("") # blank line
					lastdata[G.id] = str(Dserver.AllDservers[G.id])
			tabs -= 1
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckInvitedServers")
	
	def WriteOutDservers(self, tabs=0):
		"""Writes out the servers to their respective Server files"""
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of WriteOutDservers")
		tabs += 1
		for gid, gdict in Dserver.AllDservers.items():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Writing out Guild " + str(gid))
			serverfile = gdict["GuildFileName"]
			tabs += 1
			logger.debug(("\t" * (tabs)) + "botannouncechannel: " + str(gdict["settings"]["botannouncechannel"]))
			logger.debug(("\t" * (tabs)) + "connectionmsgid: " + str(gdict["settings"]["connectionmsgid"]))		 
			with open(DserverFilepath / Path(serverfile), 'w') as f:
				json.dump(gdict, f)
			#print("Writing out players: " + str(gdict["players"]))
			tabs -= 1
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of WriteOutDservers")
