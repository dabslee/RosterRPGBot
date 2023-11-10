from config import *
import logging
import inspect
import time
import pytz
import copy
import asyncio
import datetime
import Commands
from GameData import *
from InternalFuncs import *
from discord import Embed, utils, DiscordException, NotFound, ChannelType, ext
	
async def StartHere(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of StartHere")
	tabs += 1
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Data received: ")
	# for key, item in msg.items():
	# 	if key != "ss":
	# 		logger.debug(tb(tabs+1) + key + ": {")
	# 		deeplogdict(item, "debug", tabs+1)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " After StartHere Data Output")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " uargs: " + " ".join(msg["uargs"]))
		
	# Easy access variables
	ctx 		= msg["ctx"]
	SS 			= msg["ss"]	
	guildobj 	= msg["guild"]
	authorobj	= msg["author"]
	serverdata 	= msg["serverdata"]
	uargs 		= msg["uargs"]
	numargs		= msg["numargs"]
	AC 			= msg["ac"]
	
	outputtup = (ctx, "")
	
	# Test that given command is usable
	if msg["numargs"] == 0 or uargs[0].lower() in ["help", "commands", ]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only given !roster and nothing else. Outputting commands and exiting")
		return await AC["function"](msg) 
		
	# Clean uargs text of malicious characters
	logger.debug(tb(tabs) +  "Cleaning input of malicious characters")
	whole = "".join(uargs)
	logger.debug(tb(tabs+1) + "whole command given: " + whole)
	tabs += 1
	for char in MALICIOUS:
		logger.debug(tb(tabs) +  "testing string for malicious char: " + char)
		if char in whole:
			logger.warning(tb(tabs+1) +  "Malicious character " + char + " detected!")
			print("Malicious character " + char + " detected: " + " ".join(uargs))
			outputmsg =  "Do not use the " + char + " character"
			return (ctx, outputmsg)
		else:
			logger.debug(tb(tabs+1) + char + " not found in " + whole)
	tabs -= 1
	
	# Getting user Authority
	logger.debug(tb(tabs) +  "Getting the user's authority/priv")
	msg["authority"] = GetAuthorAuthority(guildobj, authorobj, SS["settings"]["roles"], tabs)
	
	# Check they aren't explicitly disallowed
	if msg["authority"] == 4:
		logger.debug(tb(tabs+1) + "User has authority 4 (excluded from bot use)")
		return (ctx, "You don't have authority to use RosterBot")

	# Now calling the function for the command, or none if no match
	logger.debug(tb(tabs) +  "Running through command tree")
	command = uargs[0]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " command is " + command + ", uargs is " + str(uargs))
	if command == "settings":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling the settings function") # Has to have the "function" dictionary item or it replaces all the other functions
		outputtup = AC[command]["function"](msg, tabs)	
	elif command != "gameid" and command in AC:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling an explicit function")
		if asyncio.iscoroutinefunction(AC[command]):
			outputtup = await AC[command](msg, tabs)
		else:
			outputtup = AC[command](msg, tabs) # Call the GetSet Function		
	elif command != "gameid" and command in serverdata["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling a gameid function")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " inserting gameid into the uargs")
		msg["uargs"].insert(0, "gameid")
		msg["numargs"] = len(msg["uargs"])
		command = "gameid"
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " uargs now: " + str(uargs))
		outputtup = await AC["gameid"]["function"](msg, tabs)
	else:
		logger.debug(tb(tabs) + command + " doesn't match a rosterbot command or game id")
		outputtup = (ctx, command + " doesn't match a rosterbot command or game id. Use the following command for help:\n!rb")
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StartHere")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
	return outputtup

async def DirectMessage(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of DirectMessage")
	tabs += 1
	
	outputtup = (None, "")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of DirectMessage")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " outputtup: " + str(outputtup))	
	return outputtup
# ~~~~~~~~~~~~~~~~~~~~~~~~ Server Owner Command Functions

# ~~~ Server Settings

def GSSettings(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSSettings")
	tabs += 1
	
	# Easy access variables
	# guildobj 		= msg["guild"]
	# serverdata 	= msg["serverdata"]
	SS 				= msg["ss"]
	AC				= msg["ac"]
	authorobj		= msg["author"]
	ctx 			= msg["ctx"]
	uargs 			= msg["uargs"]
	numargs 		= msg["numargs"]
	priv			= msg["authority"]		# int for the author's authority level
	command			= uargs[0]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " AC: " + str(AC))
	# Process Aliases
	if command == "setting":
		uargs[0] == "settings"
		command = uargs[0]
		msg["uargs"] = uargs
	if len(uargs) > 1 and uargs[1] == "role": # depluralising
		uargs[1] == "roles"
		msg["uargs"] = uargs	
		
	outputtup = (ctx, "No matching setting given")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority to get/set settings")
	Authorised = AuthorityCheck(SS, authorobj, "settings", priv, command, tabs=tabs)
	if Authorised[0] != True:
		outputtup = (ctx, Authorised[1])
	elif numargs == 1:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting all settings")
		outputtup = OutputAllSettings(msg, tabs)
	elif uargs[1] in SS[command]:
		logger.debug(tb(tabs+1) + "Calling a Settings Getsetter: " + uargs[1])

		if type(AC[command][uargs[1]]) == dict and "function" in AC[command][uargs[1]]:
			logger.debug(tb(tabs+1) + "function: " + str(AC[command][uargs[1]]["function"]))
			outputtup = AC[command][uargs[1]]["function"](msg, tabs)
		else:
			logger.debug(tb(tabs+1) + "function: " + str(AC[command][uargs[1]]))
			outputtup = AC[command][uargs[1]](msg, tabs)
	

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSSettings")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
	return outputtup	
			
def OutputAllSettings(msg, tabs=0):
	""" Sends all settings formatted into a message to discord """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of OutputAllSettings")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " SS: " + str(msg["ss"]))
	
	# Easy access variables
	# guildobj 		= msg["guild"]			# the discord guild object
	Serv 			= msg["serverdata"]		# my data dictionary for this guild
	SS 				= msg["ss"]				# the "server settings" dictionary for this guild
	AC 				= msg["ac"]				# the generic "all commands" dictionary for the bot
	# authorobj		= msg["author"]			# the discord member object
	uargs 			= msg["uargs"]			# the words given by the author
	# numargs 		= msg["numargs"]		# int for the number of words given
	priv			= msg["authority"]		# int for the author's authority level
	ctx 			= msg["ctx"]			# the context bot thing
	command 		= uargs[0]
			
	result = ""
	if len(uargs) == 1:
		result += "All RosterRPG Settings:\n"	
		for subc in SS["settings"].keys():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " subc is " + subc)
			data = SS[command][subc]
			if type(data) == dict or type(data) == type(AutoVivification()):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking a dict")
				if "current" in data:
					logger.debug(tb(tabs+1) + "Outputting a variable")
					result += subc + ": " + str(SS[command][subc]) + "\n"
				else:
					logger.debug(tb(tabs+1) + "Going through another dict")
					for each in data.keys():
						logger.debug(tb(tabs+1) + str(subc) + ": " + str(SS[command][subc][each]))
						result += subc + " " + each + ": " + str(SS[command][subc][each]) + "\n"
			else:
				logger.debug(tb(tabs+1) + str(subc) + ": " + str(SS[command][subc]))
				result += subc + ": " + str(SS[command][subc]) + "\n"

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of OutputAllSettings")
	return (ctx, result)

def GSAuthority(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSAuthority")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	numargs 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	subc		= uargs[1]
	
	outputtup = (ctx, "No matching " + command + " " + subc + " setting given")
	
	# Get all
	if numargs == 2: 
		logger.debug(tb(tabs+1) + "Getting all Authority levels")
		auths = SS[command][subc].keys()
		logger.debug(tb(tabs+1) + "auths: " + str(auths))
		output = "Authority levels:\n"
		if "function" in auths:
			auths.remove("function")
		auths = sorted(auths)
		for each in auths:
			output += "\t" + SS[command][subc][each] + ": \t" + each + '\n'
		outputtup = (ctx, output)
	else:
		logger.debug(tb(tabs+1) + "Getting specific Authority level: " + uargs[2])
		if uargs[2] not in SS[command][subc]:
			logger.debug(tb(tabs+1) + "No matching setting " + uargs[2] + " given")
			outputtup = (ctx, "No matching " + command + " " + subc + " " + uargs[2] + " setting given")
		elif numargs == 3:
			outputtup = (ctx, subc + " " + uargs[2] + ": " + SS[command][subc][uargs[2]])
		elif uargs[3] not in ["0", "1", "2", "3", "4"]:
			logger.debug(tb(tabs+1) + "Wrong format for setting given: " + uargs[3])
			outputtup = (ctx, "Authority level must be 1, 2, 3, or 4")
		else:
			logger.info('\t\t' + "Changing " + command + " " + subc + " " + uargs[2] + " from " + SS[command][subc][uargs[2]] + " to " + uargs[3])
			SS[command][subc][uargs[2]] = uargs[3]
			outputtup = (ctx, subc + " " + uargs[2] + " is now set to " + SS[command][subc][uargs[2]])
			
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSAuthority")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
	return outputtup	
		
def GSRoles(msg, tabs=0):
	""" Translates Role IDs to Role Names and sends back to user """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSRoles")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	numargs 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	subc		= uargs[1]

	outputtup = (ctx, "No matching " + command + " " + subc + " role given")
	
	#~~~~~~~ Getting
	if numargs == 2:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting all roles")
		text = "Guild Roles per Authority Level:\n"
		
		# Naming guild owner
		text += "0 " + guildobj.owner.mention + " (Server Owner)"
		tabs += 1
		for each in range(1,5):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting authority level " + str(each))
			text += '\n' + str(each) + " "
			for role in SS[command][subc][str(each)]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting role: " + str(role))
				roleobj = guildobj.get_role(int(role))
				text += roleobj.mention + " "
			if len(SS[command][subc][str(each)]) == 0:
				if str(each) in ["2", "3"]:
					text += guildobj.default_role.mention
				else:
					text += "no-one"
		tabs -= 1
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + text)
		return (ctx, text)
	elif numargs == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting a specific role level: " + uargs[2])
		if uargs[2] == "refresh":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing obsolete guild roles")
			tabs += 1
			for each in range(1,5):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority level " + str(each) + " for deleted guild roles")
				for num in len(SS[command][subc][str(each)]):
					role = SS[command][subc][str(each)]
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking role: " + str(role))
					roleobj = guildobj.get_role(role)
					if roleobj == None:
						logger.debug(tb(tabs+1) + "Deleting roleid " + str(role))
						SS[command][subc][str(each)].remove(role)
						num = num-1
				if len(SS[command][subc][str(each)]) == 0:
					if uargs[2] in ["2", "3"]:
						text += guildobj.default_role.mention
					else:
						text += "no-one"						
			text = "Removing deleted guild roles is complete"
			tabs -= 1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + text)
			return (ctx, text)				
		elif uargs[2] != "function" and uargs[2] in SS[command][subc]:			
			text = "Guild Roles for Authority Level " + uargs[2] + ": "
			tabs += 1
			for role in SS[command][subc][uargs[2]]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting role: " + str(role))
				roleobj = guildobj.get_role(int(role))
				text += roleobj.mention + " "
			if len(SS[command][subc][uargs[2]]) == 0:
				if uargs[2] in ["2", "3"]:
					text += guildobj.default_role.mention
				else:
					text += "no-one"
			tabs -= 1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + text)
			return (ctx, text)		

	#~~~~~~~ Setting
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting role level " + uargs[2])
	
	# Validate given variable
	if uargs[2] != "function" and uargs[2] not in SS[command][subc]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching authority level given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
		return (ctx, authorobj.mention + " No matching authority level given")
	
	# Get current data and given roles
	current = SS[command][subc][uargs[2]]
	roles = ctx.message.role_mentions
	
	if len(roles) == 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No roles mentioned")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
		return (ctx, authorobj.mention + " Please @mention a valid discord server role")
	text = ""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roles as mentions: " + str(roles))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Current as IDs: " + str(roles))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Going through each role mentioned")
	for each in roles:
		tabs += 1
		logger.debug(tb(tabs+1) + "Checking " + each.name)
		rid = str(each.id)
		if rid in current:
			logger.debug(tb(tabs+1) + "Removed " + each.name)
			SS[command][subc][uargs[2]].remove(rid)
			text += "Removed " + each.mention + " to Authority Level " + uargs[2] + '\n'
		else:
			logger.debug(tb(tabs+1) + "Added " + each.name)
			SS[command][subc][uargs[2]].append(rid)
			text += "Added " + each.mention + " to Authority Level " + uargs[2] + '\n'
		tabs -= 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSRoles")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output " + text)
	return (ctx, text	)
	
def GSDeleteListingsTimer(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSDeleteListingsTimer")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	if args > 3: # Too many arguments given
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " More than 3 arguments given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSDeleteListingsTimer")
		return (ctx, authorobj.mention + " "	)
	elif args == 3:
		
		# Check that the arg given can be converted to int
		try:
			int(uargs[2])
		except ValueError:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to an int but couldn't (not an string that can be converted to in)")
			return (ctx, "") 
		
		if int(uargs[2]) < -1:
			uargs[2] = "-1"
			
		if int(uargs[2]) == 0:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to 0")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSDeleteListingsTimer")
			return (ctx, authorobj.mention + " Number must be -1 for no timer or greater than 0")
		else:
			SS[command][subc] = int(uargs[2])
			logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSDeleteListingsTimer")
	logger.debug(tb(tabs) + str(SS[command][subc].keys()))
	return (ctx, subc + " is set to " + str(SS[command][subc]) + " minutes. (Note: Set to -1 to disable deletion timer)")

def ResetPriorities(msg, tabs=0):
	""" Gathers a list of users who need to be updated"""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ResetPriorities")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
	Authorised = AuthorityCheck(SS, authorobj, "resetpriorities", priv, uargs[0], tabs=tabs)
	if Authorised[0] != True:
		outputtup = (ctx, Authorised[1])
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Going through all players and resetting priority")
	for pid, each in Serv["players"].items():
		ResetPlayerPriorities(pid, each, tabs+1)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ResetPriorities")
	return (ctx, authorobj.mention + " Priorities have been reset for all players. This is irreversible! Note: \nIf you have automatic reset turned on, this has not reset the time of nextpriorityreset.")
		
# ~~~ Discord Channel Settings
def GSBotannouncechannel(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSBotannouncechannel")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]
	
	text = ""
	
	if args >= 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting botannouncechannel with " + uargs[2])
		# Check that the arg given is a channel
		if len(ctx.message.channel_mentions) == 0:
			logger.debug(tb(tabs+1) + "No channels mentioned")
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Going through each channel mentioned")
			for each in ctx.message.channel_mentions:
				logger.debug(tb(tabs+1) + "Checking " + each.name)
				cid = str(each.id)
				if cid in SS[command][subc]:
					logger.debug(tb(tabs+1) + "Removing " + each.name)
					SS[command][subc].remove(cid)
					text += "Removed " + each.mention + " from " + subc + '\n'
				else:
					logger.debug(tb(tabs+1) + "Adding " + each.name)
					SS[command][subc].append(cid)
					text += "Added " + each.mention + " to " + subc + '\n'
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)
	
	if len(SS[command][subc]) == 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Channel set to None")
		text += subc + " is set to none"
	else:
		logger.debug(tb(tabs) + command + " " + subc + " set to " + str(SS[command][subc]))
		
		text += subc + " is set to: "
		for each in SS[command][subc]:
			text += guildobj.get_channel(int(each)).mention + " "
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputtup is " + text)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSBotannouncechannel")
	return (ctx, text)

def GSGMsOnlyEditOwn(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSGMsOnlyEditOwn")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	text = ""
	if args >= 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting GMsOnlyEditOwn with " + uargs[2])
		# Check that the arg given is a channel
		if uargs[2].lower() in TOGGLEON:
			SS["settings"]["gmsonlyeditown"] = "1"
			text = "gmseditonlyown is now true"
		elif uargs[2].lower() in TOGGLEOFF:
			SS["settings"]["gmsonlyeditown"] = "0"
			text = "gmseditonlyown is now true"
		else:
			text = authorobj.mention + " Please use the following settings: " + " ".join(TOGGLEOFF) + " " + " ".join(TOGGLEON)
	else:
		text = "gmseditonlyown is currently " + TOGGLEFT[int(SS["settings"][subc])]
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSGMsOnlyEditOwn")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " text: " + text)
	return (ctx, text)

def GSPrioritiesOn(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSprioritieson")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	text = ""
	if args >= 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting GSprioritieson with " + uargs[2])
		# Check that the arg given is a channel
		if uargs[2].lower() in TOGGLEON:
			SS["settings"][subc] = "1"
			text = "prioritieson is now true"
		elif uargs[2].lower() in TOGGLEOFF:
			SS["settings"][subc] = "0"
			text = "prioritieson is now false"
		else:
			text = authorobj.mention + " Please use the following settings: " + " ".join(TOGGLEOFF) + " " + " ".join(TOGGLEON)
	else:
		text = "prioritieson is currently " + TOGGLEFT[int(SS["settings"][subc])]
	text += '\nNOTE: This setting has no effect yet'
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSprioritieson")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " text: " + text)
	return (ctx, text)

def GSLevelCapsOn(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSLevelCapsOn")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	text = ""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " SS[settings][subc] current: " + str(SS["settings"][subc]))
	if args >= 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting GSLevelCapsOn with " + uargs[2])		
		# Check that the arg given is a channel
		if uargs[2].lower() in TOGGLEON:
			SS["settings"][subc] = "1"
			text = "levelcapson is now true"
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to On")
		elif uargs[2].lower() in TOGGLEOFF:
			SS["settings"][subc] = "0"
			text = "levelcapson is now false"
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to Off")
		else:
			text = authorobj.mention + " Please use the following settings: " + " ".join(TOGGLEOFF) + " " + " ".join(TOGGLEON)
	else:
		text = authorobj.mention + " levelcapson is currently " + TOGGLEFT[int(SS["settings"][subc])]
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSLevelCapsOn")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " text: " + text)
	return (ctx, text)

def GSNextPriorityReset(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSNextPriorityReset")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]
	current 	= SS["settings"]["nextpriorityreset"]
	outputmsg 	= "Next priority reset is scheduled for UTC " + current
	output 		= (ctx, outputmsg)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting author's tz")
	tz = Serv["players"][str(authorobj.id)]["tz"]
	if tz in ["", None]:
		tz = "UTC"
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if a timezone was given")
	dtpos = 3 # from which index the dt starts at (if setting)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " args: " + str(args))
	tzgiven = False
	if args > 2 and uargs[2] in pytz.all_timezones:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Was given one: " + uargs[2])
		if uargs[2] != "GMT" and ("GMT+" in uargs[2] or "GMT-" in uargs[2]):
			output = (ctx, authorobj.mention + " Please use a valid timezone other than GMT+ or GMT-")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + str(output))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSNextPriorityReset")
			return output
		tz = uargs[2]
		tzgiven = True
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not given one")
		dtpos = 2
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " tz now: " + str(tz))
				
	if (tzgiven and args == 3) or (tzgiven == False and args == 2):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only getting the next priority reset date")
		if current == "":
			output = (ctx, authorobj.mention + " nextpriorityreset is unset")
		else:
			dt = ConvertTimezone("UTC", current, tz, fromformat=TFORMAT, toformat=TFORMAT, tabs=0)
			if type(dt) == type(""):
				output = (ctx, authorobj.mention + " " + outputmsg + " (or in your given timezone: " + tz + " " + dt + ")")
			else:
				output = (ctx, authorobj.mention + " " + DTERROR)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Trying to set a new datetime")	
		newdt = " ".join(uargs[dtpos:])
		result = SetNextPriorityReset(Serv, tz, newdt, 0, tabs)
		output = (ctx, authorobj.mention + " " + result)
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + str(output))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSNextPriorityReset")
	return output

def GSPriorityResetFreq(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSPriorityResetFreq")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]
	
	nextwasreset = False
	if args > 3: # Too many arguments given
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " More than 3 arguments given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMax")
		return (ctx, "") 
	elif args == 3: # settings priorityresetfreq x
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting PriorityResetFreq")
		# Check that the arg given can be converted to int
		newvar = uargs[2]
		if newvar.lower() in TOGGLEOFF:
			newvar = "0"
		asnum = StrToNumber(newvar, tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " asnum: " + str(asnum))
		if asnum != "":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Is a number")								
			if asnum < 0:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Was less than 0")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPriorityResetFreq")
				return (ctx, authorobj.mention + " Please provide a number: \n- 0 for no automatic resets \n- greater than 0 for the number of days between resets")

			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting to " + uargs[2])
			SS[command][subc] = uargs[2]
			logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
			logger.debug(tb(tabs) +"nextpriorityreset currently: " + str(SS["settings"]["nextpriorityreset"]))
			if asnum > 0 and SS["settings"]["nextpriorityreset"] in ["", None]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " nextpriorityreset was blank so setting a new value")
				result = SetNextPriorityReset(Serv, "UTC", "", asnum, tabs)
			elif asnum == 0: 
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Was turned off. Blanking nextpriorityreset") # Need to do this in case it gets turned on again and resets immediately because next reset is in the past
				SS["settings"]["nextpriorityreset"] = ""
			else:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " frequency just changed to another number. Keeping current nextpriorityreset")
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to an int but couldn't (not an string that can be converted to int or float)")
			return (ctx, authorobj.mention + " Can't set " + subc + " as " + uargs[2] + " is not a number")			
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting author's tz")
	tz = Serv["players"][str(authorobj.id)]["tz"]
	if tz in ["", None]:
		tz = "UTC"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting stored UTC nextconverted to player's tz")
	nextconverted = SS["settings"]["nextpriorityreset"]
	if nextconverted not in ["", None]:
		nextconverted = ConvertTimezone("UTC", nextconverted, tz, fromformat=TFORMAT, toformat=TFORMAT, tabs=tabs)
	else:
		tz = ""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " nextconverted: " + str(nextconverted))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPriorityResetFreq")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now set to: " + str(SS[command][subc]))
	message = authorobj.mention + " " + subc + " is set to " + str(SS[command][subc]) + " day/s"
	message += "\n\tNote: Set to 0 to disable"	
	message += "\n\tnextpriorityreset is currently:\t" + tz + " " + StrOrUnset(nextconverted)
	message += "\n\tChanging the frequency to 0 will clear nextpriorityreset"
	message += "\n\tChanging to another number won't change nextpriorityreset"
	message += "\n\tIf necessary, please update nextpriorityreset manually with"
	message += "\n\t!rb settings nextpriorityreset"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + str((ctx, message)))
	return (ctx, message)

def GSPriorityResetMsg(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSPriorityResetMsg")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]
	current 	= SS[command][subc]
	
	message = authorobj.mention + " " + subc + " is:\n" + StrOrUnset(current)
	if args > 2:		
		# Check that the arg given can be converted to int
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting a new message")
		new = " ".join(uargs[2:])
		SS[command][subc] = new
		logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
		message = authorobj.mention + " " + subc + " was\n" + StrOrUnset(current) + "\nand is now\n" + StrOrUnset(SS[command][subc])
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPriorityResetMsg")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " New message: " + message)
	return (ctx, message)

# ~~~ Per-Game Settings

def GSPlayerMaxConsecutive(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSPlayerMaxConsecutive")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	if args > 3: # Too many arguments given
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " More than 3 arguments given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMaxConsecutive")
		return (ctx, authorobj.mention + " "	)
	elif args == 3:
		
		# Check that the arg given can be converted to int
		data = None
		try:
			data = int(uargs[2])
		except ValueError:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to an int but couldn't (not an string that can be converted to in)")
			return (ctx, authorobj.mention + " Can't set " + subc + " as " + uargs[2] + " is not a number")
		SS[command][subc] = uargs[2]
		logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMaxConsecutive")
	logger.debug(tb(tabs) + str(SS[command][subc]))
	return (ctx, subc + " is set to " + str(SS[command][subc]) + " games.\n Set to 0 to prevent players playing one game immediately after another.\n Set to -1 to disable this restriction.\n Set to 1 to allow players to play two games in a row, etc")

def GSPlayerMax(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSPlayerMax")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	if args > 3: # Too many arguments given
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " More than 3 arguments given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMax")
		return (ctx, "") 
	elif args == 3:
		
		# Check that the arg given can be converted to int
		data = None
		try:
			data = int(uargs[2])
		except ValueError:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to an int but couldn't (not an string that can be converted to in)")
			return (ctx, authorobj.mention + " Can't set " + subc + " as " + uargs[2] + " is not a number")
					
		if int(uargs[2]) == 0:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to 0")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMax")
			return (ctx, authorobj.mention + " Number must be -1 for no timer or greater than 0")
		else:
			SS[command][subc] = uargs[2]
			logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerMax")
	logger.debug(tb(tabs) + str(SS[command][subc]))
	return (ctx, subc + " is set to " + str(SS[command][subc]) + " game/s. (Note: Set to -1 for no limit)")

def GSPlayerLevel(msg, tabs=0):
	""" Sets a basic current setting to the given args based on data type """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSPlayerLevel")
	tabs += 1
		
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	subc 		= uargs[1]

	if args > 3: # Too many arguments given
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " More than 3 arguments given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerLevel")
		return (ctx, "") 
	elif args == 3:
		
		# Check that the arg given can be converted to int
		data = None
		try:
			data = int(uargs[2])
		except ValueError:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried to set " + subc + " to an int but couldn't (not an string that can be converted to in)")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerLevel")
			return (ctx, authorobj.mention + " Can't set " + subc + " as " + uargs[2] + " is not an acceptable number")
					
			SS[command][subc] = uargs[2]
			logger.debug(tb(tabs) + subc + " now set to: " + str(SS[command][subc]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating default game data")
			if "max" in subc:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updated default max level")
				Serv["games"]["default"]["maxlevel"] = uargs[2]
			else:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updated default min level")
				Serv["games"]["default"]["minlevel"] = uargs[2]
	else: # Getting
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Retrieving " + subc)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPlayerLevel")
	logger.debug(tb(tabs) + str(SS[command][subc]))
	return (ctx, subc + " is set to " + str(SS[command][subc]))

# ~~~~~~~~~~~~~~~~~~~~~~~~ Commands for all users

async def BotInfoBox(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of BotInfoBox")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	numargs 	= msg["numargs"]		# int for the number of words given
	ctx 		= msg["ctx"]			# the context bot thing
	
	outputtup = (ctx, "")
	
	author_member = await ctx.bot.fetch_user(AUTHORID)
	data = {
		"title": 		"RosterRPG Bot",
		"description":	"Helping keeping games a-runnin!",
		"Guide": "https://docs.google.com/document/d/1Sfti81Xri9hAQrSRHpOJ1-yApn6esOPpsvgT3SYsa04/edit?usp=sharing",
	}
	infobox = Embed.from_dict(data)
	data = [
		("Author", author_member.mention),
		("Made", "2020"),
		("Guide", "https://docs.google.com/document/d/1Sfti81Xri9hAQrSRHpOJ1-yApn6esOPpsvgT3SYsa04/edit?usp=sharing"),
		("Frequently Used", "!rb games\n!rb listme\n!rb priority\n!rb newgame"),
		(":coffee: Shout me a coffee", "Once: http://paypal.me/SladeN\nMonthly: http://www.patreon.com/tehmanticore")
		]

	for each in data:
		line = True
		if each[0] == "Guide":
			line = False
		infobox.add_field(inline=line, name=each[0], value=each[1])
	infobox.color = 0xeee657	
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of BotInfoBox")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
	return (ctx, infobox)	

def PrintGameInfo(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of PrintGameInfo")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	gameid		= uargs[1]
	GameDict 	= Serv["games"]
	pid 		= str(authorobj.id)
	
	tz = None
	# Setting timezone to what was given
	edit = False
	if args == 3:
		tz = uargs[2]
	elif Serv["players"][pid]["tz"] not in ["", None]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Using author's own timezone")
		tz = Serv["players"][pid]["tz"]
	
	result = GetGameInfoEmbed(ctx.bot, Serv, gameid, tz)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PrintGameInfo")
	return (ctx, result)

def GetGames(msg, tabs=0):
	""" Prints all future, published games """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetGames")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]

	# Check aliases
	if command in ["g", ]:
		msg["uargs"][0] = "games"
		command 		= msg["uargs"][0]
		uargs 			= msg["uargs"]

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking which games requested")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")		
	Authorised = AuthorityCheck(SS, authorobj, "viewallgames", priv, command, tabs)
	if Authorised[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
		outputtup = (ctx, Authorised[1])
		return outputtup
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
			
	# Booleans to show what is wanted (which to explicitly include in results)
	# Standard is all incomplete, published games
	# These don't exclude each other
	filters		= False
	completed 	= False
	incompleted = True
	published 	= True
	unpublished	= False
	qualifier 	= ""

	if "unpublished" in uargs or "both" in uargs or "complete" in uargs or "all" in uargs:
		filters = True
		if "unpublished" in uargs or "unpub" in uargs:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Requested unpublished future games")
			unpublished = True
			published = False
			qualifier = " (Unpublished and yet to be completed) "
			if "unpublished" in uargs:
				uargs.remove("unpublished") # no longer needed
			if "unpub" in uargs:
				uargs.remove("unpub") # no longer needed
			args = len(uargs)
		elif "both" in uargs:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Requested all future games, published and unpublished")
			unpublished = True
			published = True
			qualifier = " (All incomplete) "
			if "both" in uargs:
				uargs.remove("both") # no longer needed
			args = len(uargs)
		elif "complete" in uargs or "completed" in uargs:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Requested all completed (past) games")
			unpublished = True
			published = True
			completed = True
			incompleted = False
			qualifier = " (Completed only) "
			if "complete" in uargs:
				uargs.remove("complete") # no longer needed
			if "completed" in uargs:
				uargs.remove("completed") # no longer needed
			args = len(uargs)
		elif "all" in uargs:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Requested all games")
			unpublished = True # make all true
			published = True
			completed = True
			qualifier = " (All past and future) "
			if "all" in uargs:
				uargs.remove("all") # no longer needed
			args = len(uargs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Toggles:")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " completed: \t\t" + str(completed))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " incompleted: \t\t" + str(incompleted))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " published: \t\t" + str(published))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " unpublished: \t\t" + str(unpublished))

	mygm = False
	if "mygm" in uargs:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Filtering to only those the player is GM for")
		mygm = True
		uargs.remove("mygm")
		args = len(uargs)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking for and converting timezone")	
	fgames = []
	tz = pytz.timezone('UTC')
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " tz: " + str(tz))
	reqtz = (False, "")
	if args >= 2:
		try:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Trying to convert timezone " + uargs[1])
			pytz.timezone(uargs[1])
			reqtz = (True, uargs[1])
		except (Exception, DiscordException) as e:
			edata = PrintException()
			logger.error('\t' + "There was an error converting timezone " + uargs[1])
			logger.error('\t' + str(edata))
			print("There was an error converting timezone " + uargs[1])
			print(edata)
			return (ctx, authorobj.mention + " That timezone makes no sense!")
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Testing if player has set a timezone")
		pid = str(authorobj.id)
		ptz = Serv["players"][pid]["tz"]
		if ptz not in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " tz found: " + ptz)
			reqtz = (True, ptz) 
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No timezone found or requested")
	
	glist = None
	if filters:
		glist = [name for name in Serv["games"].keys()]
		if "default" in glist:
			glist.remove("default")
	else:
		glist = Serv["activegames"][:]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Cleaning Activegames")
		for unit in glist:
			UpdateActiveGames(Serv, unit, Serv["games"][unit], tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Cleaning Activegames")
		glist = Serv["activegames"][:]		 
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Num of games = " + str(len(glist)))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " glist: " + str(glist))

	result = authorobj.mention + qualifier + " Games are"
	if reqtz[0]:
		result += " (in " + reqtz[1] + " timezone)"
	result += ":\n"
	results = []
	levellength = 0 #store size of the game level string
	spotslength = 0 #store size of the free spots column string
	
	for each in glist:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking game: " + each)
		game = Serv["games"][each]
		pubd = game["published"].lower()
		compd = game["completed"].lower()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pubd: " + str(pubd) + ", compd:" + compd)
		
		# Testing for
		if filters:
			comptest = False
			pubtest  = False
			if completed and compd in TOGGLEON:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Want completed and game IS complete")
				comptest = True
			if incompleted and compd in TOGGLEOFF:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Want incompleted and game IS incompleted")
				comptest = True
			if published and pubd in TOGGLEON:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Want published and game IS published")
				pubtest = True
			if unpublished and pubd in TOGGLEOFF:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Want unpublished and game IS unpublished")
				pubtest = True
			if False in [comptest, pubtest]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Didn't pass. Continuing")
				continue
		
		if mygm and game["gm"] != str(authorobj.id):
			continue
		
		timestr = ""
		if reqtz[0]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting to requested timezone")
			timestr = ConvertTimezone(game["timezone"], game["datetime"], reqtz[1], TFORMAT, TDFORMATSHORT, tabs)
		else:
			timestr = game["timezone"] + " " + ConvertTimezone(game["timezone"], game["datetime"], game["timezone"], TFORMAT, TDFORMATSHORT, tabs)	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting game data")
		levelstr = "L" + game["minlevel"] + " - " + game["maxlevel"]
		if len(levelstr) > levellength:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " levellength was " + str(levellength) + " and is now " + str(len(levelstr)))
			levellength = len(levelstr)
		
		gamename = game["name"]
		gamedur  = game["duration"] 
		# Calculating freespots column
		freespots = int(game["maxplayers"]) - len(game["roster"])
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Freespots: " + str(freespots))
		crl = CheckRosterLocked(game, tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " crl: " + str(crl))
		
		if game["onlygmadd"] == "1":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only GM can add players")
			freespots = "GM"
		elif float(freespots) >= 1:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Just using freespots as number")
			freespots = str(len(game["roster"])) + "/" + game["maxplayers"]
		elif crl:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roster is locked")
			freespots = "L"
		else:
			
			freespots = ""
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if there's a lower priority player")
			ps = []
			authp = CalcPlayerPriority(Serv, str(authorobj.id), tabs)
			for pl, status in game["roster"]:
				if CalcPlayerPriority(Serv, pl, tabs) > authp and status == "unfixed":
					freespots = "<"
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Freespots after: " + str(freespots))
		if len(freespots) > spotslength:
			spotslength = len(freespots)
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking whether listed to game")
		checks = ["gr", "r", "s"]
		listings = ""
		for role in checks:
			if each in Serv["players"][str(authorobj.id)][role]:
				code = role
				if role == "gr":
					code = "gm"
				listings += "| [" + code + "]"
		thisline = [each, timestr, levelstr, freespots, gamename, gamedur, listings]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game data: " + str(thisline))
		results.append(thisline)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " results: " + str(results))
	if len(results) == 0:
		result = "There are no games scheduled right now. "
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sorting results by datetime")
		results = sorted(results, key = lambda x: x[1])
		
		for each in results:
			result += "`" + each[0]
			result += " " * (15 - len(each[0]))
			result += each[1] + "  "
			result += each[2] + (" " * (levellength - len(each[2]))) 
			result += " " * 2
			result += each[3] + (" " * (spotslength - len(each[3]))) + "  "
			result += each[4]  + "  "
			result += "{" + each[5] + "} "
			result += each[6] + "`\n"
	result += "Use !rb <game id> for more info"

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PrintFutureGames")
	return (ctx, result)

def GetPriority(msg, tabs=0):
	""" Returns the P# and list of games """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetPriority")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	
	# Check aliases
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking aliases")
	if command in ["prio", "p"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Aliases found. Replacing")
		msg["uargs"][0] = "priority"
		command 		= msg["uargs"][0]
		uargs 			= msg["uargs"]
		
	# Make sure given value is valid
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if a member was mentioned")
	member = None
	if len(ctx.message.mentions):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " A member was mentioned")
		member = ctx.message.mentions[0]
	elif args == 1 or uargs[1].lower() in ["me",]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting member as author")
		member = ctx.message.author
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Searching for member with given name")
		members = [m for m in guildobj.members if m.display_name.lower() == uargs[1].lower()]
		member = None
		if len(members):
			member = members[0]			
	
	if member == None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching player found for arg " + str(uargs[1]))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetPlayerPriority")
		return (ctx, authorobj.mention + " No matching player found")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
	if member != ctx.message.author:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority to view other members' priorities")
		
		Authorised = AuthorityCheck(SS, authorobj, "viewpriorities", priv, command, tabs)
		if Authorised[0] == False:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
			outputtup = (ctx, Authorised[1])
			return outputtup
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")		
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting priority")
	pid = str(member.id)
	data = Serv["players"][pid]
	priority = CalcPlayerPriority(Serv, pid, tabs)
	if priority % 1 == 0: # Remove decimal place if not needed
		priority = int(priority)
	result = "Priority level for " + member.display_name + " is " + str(priority)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting timezone data")
	tz = None
	if args == 3 and uargs[2] in pytz.all_timezones:
		tz = uargs[2]
	elif data["tz"] not in ["", None]:
		tz = data["tz"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " tz: " + str(tz))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Looping through game sets")
	gamesets = [
		("r", "Rostered Games:"),
		("gr", "Upcoming Game Mastering:"),
		("s", "Sidelined Games:"),
		("p", "Played Games: (each adds to your Priority)"),
		("gp", "Game Mastered Games:"),
		("l", "Games played last week:")
		]
	logger.debug(tb(tabs) + str(data.items()))
	for setnum, (letter, name) in enumerate(gamesets):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking setnum: " + str(setnum) + ", letter: " + str(letter) + ", name: " + str(name))
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking that game exists and wasn't deleted")
		logger.debug(tb(tabs) + str(len(data[letter])) + " letter games: " + str(data[letter]))
		for order, gamename in list(enumerate(data[letter][:]))[::-1]: #gotta enumerate, convert to list, THEN reverse it
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking " + str(order) + " " + str(gamename))
			if gamename not in Serv["games"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game has been deleted. Removing from record")
				del data[letter][order]
		
		if len(data[letter]):
			result += "\n " + name + "\n"
			results = []
			for num, game in enumerate(data[letter]):
				logger.debug(tb(tabs+1) + "Checking num: " + str(num) + ", game: " + str(game))
				resettz = False
				if tz in ["", None] or resettz:
					logger.debug(tb(tabs+2) + "Using game's timezone")
					tz = Serv["games"][game]["timezone"]
					logger.debug(tb(tabs+2) + "tz: " + str(tz))
					resettz = True
				levelstr = "L" + Serv["games"][game]["minlevel"] + " - " + Serv["games"][game]["maxlevel"]
				thisline = [game, GetGameDateTime(Serv, game, tz, tabs), levelstr, Serv["games"][game]["name"], Serv["games"][game]["priorityamt"]]
				results.append(thisline)
				if resettz:
					tz == None
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Formatting lines")
			results = sorted(results, key = lambda x: x[1])
			
			for num, each in enumerate(results):
				result += "`\t" + str(num+1)  + ". " 	# Number
				if len(data[letter]) > 9 and num+1 < 10:
					result += " "
				result += each[0] + " " * (15 - len(each[0])) # gameid
				result += each[1] + "\t"  # datetime 
				result += each[2] + " " * (10 - len(each[2])) # level and gap
				result += each[3]  + " (+"
				result += each[4] + ")" + "`\n"	 # game name
	
	if Serv["settings"]["priorityresetfreq"] != "0" and Serv["settings"]["nextpriorityreset"] not in ["", None]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding a line about the next priority reset")
		if tz in ["", None]:
			logger.debug(tb(tabs+1) + "User hasn't set their tz yet. Setting to UTC")
			tz = "UTC" #need to set this in case someone that hasn't set their timezone calls for their priority			
		nextreset = ConvertTimezone("UTC", Serv["settings"]["nextpriorityreset"], tz, fromformat=TFORMAT, toformat=TDFORMAT, tabs=tabs)
		result += "\nThe next priority reset is scheduled for:\t`" + tz + " " + nextreset + "`"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetPriority")
	return (ctx, result)

def PrintTimezones(msg, tabs=0):
	""" Prints Help on making a new game """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of PrintTimezones")
	tabs += 1
	
	# Easy access variables
	authorobj	= msg["author"]			# the discord member object
	
	tzs = ""
	for tz in pytz.all_timezones:
		if "Etc/" not in tz:
			tzs += tz + "\n"
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PrintTimezones")
	return (authorobj, tzs)

def GSMyTimezone(msg, tabs=0):
	""" Allows the player to set and edit their own timezone """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSMyTimezone")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	pid 		= str(authorobj.id)
	
	# Check for aliases and misspellings
	if command.lower() in ["mytz", "tz", ]:
		logger.info('\t\t' + "Fixing alias: " + command)
		uargs[0] = "mytimezone"
		command		= uargs[0]
	else:
		logger.debug(tb(tabs+1) + "No aliases found")

	logger.debug(tb(tabs+1) + "Checking for current and Initialising if absent")
	if "tz" not in Serv["players"][pid].keys():
		logger.debug(tb(tabs+1) + "Initialising missing variable")
		Serv["players"][pid]["tz"] = ""
	current = Serv["players"][pid]["tz"]
	if current in ["", None]:
		current = "unset"
	logger.debug(tb(tabs+1) + "Current is " + current)
	
	# check authority level
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
	Authorised = AuthorityCheck(SS, authorobj, "mytimezone", priv, command)
	if Authorised[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
		outputtup = (ctx, Authorised[1])
		return outputtup
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
	
	# Get
	if args == 1:
		logger.debug(tb(tabs+1) + "End of GSMyTimezone")
		return (ctx, authorobj.mention + " Your timezone is " + current)
	
	# Make sure given value is valid
	logger.debug(tb(tabs+1) + "Validity check")
	new = uargs[1]
	logger.debug(tb(tabs+1) + "New variable is " + new)
	if "etc/gmt" in new.lower() or new not in pytz.all_timezones:
		logger.debug(tb(tabs+1) + "Tried to use the broken etc/gmt zones OR couldn't find a correct tz")
		logger.debug(tb(tabs+1) + "End of GSMyTimezone")
		return (ctx, authorobj.mention + " " + new + " not found. Please double check the list of timezones using !rb alltimezones")		

	
	# Set
	outputtup = (ctx, authorobj.mention + " Timezone was " + current + " and now set to " + new)
	logger.debug(tb(tabs+1) + "Setting new var")
	Serv["players"][pid]["tz"] = new
	
	logger.debug(tb(tabs+1) + "End of GSMyTimezone")
	return outputtup

async def ListMe(msg, tabs=0):
	""" Listing self for a game roster and sideline """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ListMe")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	
	gameid = None
	gamedict = None
	if command in Serv["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid is " + command)
		gameid = command
		gamedict = Serv["games"][gameid]
	elif args > 1 and uargs[1] in Serv["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid is " + uargs[1])
		gameid = uargs[1]
		gamedict = Serv["games"][gameid]
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No gameid given")
		return (ctx, authorobj.mention + " Please provide a valid gameid to list for")
	
	# Checking if game is published or complete
	if gamedict["published"] == "0":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Can't unlist from a completed game")
		return (ctx, authorobj.mention + " You can't list for an unpublished game")

	team = "both"
	
	if "rosterme" in uargs:
		team = "roster"
	elif "sidelineme" in uargs: 
		team = "sideline"
	
	outputlist = []
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if roster is locked")
	if CheckRosterLocked(gamedict, tabs) and len(gamedict["roster"]) >= int(gamedict["maxplayers"]):
		logger.debug(tb(tabs+1) + "Roster is locked from new additions")
		thisoutput = (ctx, authorobj.mention + " The roster is locked from changes now. Checking if you can be added to sidelines...")
		outputlist.append(thisoutput)
		team = "sideline"
	else:
		logger.debug(tb(tabs+1) + "Roster isn't locked from new additions")
		
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if only GMs can add players")
	if team in ["both", "roster"] and gamedict["onlygmadd"] == "1":
		logger.debug(tb(tabs+1) + "Roster is locked from new additions")
		thisoutput = (ctx, authorobj.mention + " This roster can only have players added by the GM. Checking if you can be added to sidelines...")
		outputlist.append(thisoutput)
		team = "sideline"
	else:
		logger.debug(tb(tabs+1) + "Roster isn't locked from player additions")
		
	status = "unfixed"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Figuring out whether to use fixed status")
	authname = "rosterfixed"
	usefixed = False
	if "fixed" in uargs:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Explicitly requested fixed status")
		usefixed = True
	
	if "sidelineme" in uargs and "rosterme" not in uargs and "listme" not in uargs: # can't have peeps adding "sidelineme" to the end of commands to override this
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Called sidelineme")
		authname 	= "sidelinefixed"
		status 		= "fixed"
		usefixed	= True
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Usefixed: " + TOGGLEFT[usefixed])
	auth = Serv["settings"]["authority"][authname]		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " auth: " + str(auth))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority to use fixed status")
	if usefixed and priv > int(auth):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " User doesn't have permission to set status to fixed")
		output = (ctx, authorobj.mention + " You don't have permission to " + team + " yourself as \"fixed\". Listing as unfixed")
		outputlist.append(output)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Status allowed to be set to fixed")
		if usefixed:
			status = "fixed"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " status: " + status)
	
	output = await ListPlayer(ctx, Serv, SS, authorobj, gamedict, priv, listing=team, fixed=status, whisper=False, tabs=tabs)
	if type(output) == type([]):
		outputlist = outputlist + output
	else:
		outputlist.append(output)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListMe")
	return (ctx, "List of outputups", outputlist)

async def UnlistMe(msg, tabs=0):
	""" Unlisting self for a game roster and sideline """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UnlistMe")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command		= uargs[0]
	
	gameid = None
	gamedict = None
	if command in Serv["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid is " + command) # format: !rb <gameid> unlistme
		gameid = command
		gamedict = Serv["games"][gameid]
	elif args > 1 and uargs[1] in Serv["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid is " + uargs[1]) #format: !rb unlistme <gameid>
		gameid = uargs[1]
		gamedict = Serv["games"][gameid]
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No gameid given")
		return (ctx, authorobj.mention + " Please provide a valid gameid to list for")
	
	# Checking if game is published or complete
	if gamedict["completed"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Can't unlist from a completed game")
		return (ctx, authorobj.mention + " You can't unlist from a completed game")

	outputlist = []
	listing = "both"
	if "unrosterme" in uargs:
		listing = "roster"
	elif "unsidelineme" in uargs:
		listing = "sideline"
	output = await UnlistPlayer(ctx, Serv, SS, authorobj, gamedict, priv, unlisting=listing, whisper=False, movefixed=True, tabs=tabs)
	if type(output) == type([]):
		outputlist = outputlist + output
	else:
		outputlist.append(output)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UnlistMe")
	return (ctx, "List of outputups", outputlist)

async def ListPlayer(ctx, ServData, SS, memberobj, gamedict, priv, listing="both", fixed="unfixed", whisper=False, tabs=0):
	""" Adds a player to either the Roster or Sidelines for a game """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ListPlayer")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Data received:")
	for each in [("ctx", ctx), ("member", memberobj), ("member.id", str(memberobj.id)), ("gameid", gamedict["id"]), ("priv", priv), ("listing", listing), ("fixed", fixed)]:
		logger.debug(tb(tabs) + each[0] + ": " + str(each[1]))

	gameid  = gamedict["id"]
	pid		= str(memberobj.id)
	outputlist = []
	chan = ctx
	if whisper and not memberobj.bot:
		chan = memberobj
		
	# Switching memberobj FROM a User object to a MEMBER object specific to the guild)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " memberobj was: " + str(memberobj))
	memberobj = ctx.guild.get_member(memberobj.id)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " memberobj is now: " + str(memberobj))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking how many times to loop through this function")	
	sendtosideline = False # whether to call ListPlayer>sideline after this
	other = "sideline"
	if listing == "both":
		logger.debug(tb(tabs+1) + "Looping for Roster AND Sideline")
		sendtosideline = True
		listing = "roster"
	elif listing == "sideline":
		logger.debug(tb(tabs+1) + "Just going through sideline")
		other = "roster"
	else:
		logger.debug(tb(tabs+1) + "Just going through roster")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " listing: " + listing + ", other: " + other)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " current player " + listing + ": " + str(gamedict[listing]))
				 
	# Step 0 - Check if Sidelines is on
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 0 - Check if Sidelines is on")
	if listing == "sideline" and gamedict["sidelineson"] == "0":
		logger.debug(tb(tabs+1) + "Sidelines isn't on")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
		return (ctx, memberobj.mention + " There are no sidelines allowed for game " + gameid)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 0 Passed")

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 0.5 - Get the authority to use fixed status")
	fixedauth = False
	authname = "rosterfixed"
	if listing == "sideline":
		authname = "sidelinefixed"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " authname: " + str(authname))
	fixedauth = AuthorityCheck(SS, ctx.message.author, authname, priv, "settings", subc="authority", gamedict=gamedict, tabs=tabs)[0]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " fixedauth: " + str(fixedauth))
	
	# Step 1 - Check if player is in current list
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1 - Check if player is in current list")
	pids = [pl[0] for pl in gamedict[listing]]
	if pid in pids:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is in " + listing + " list")
		pos = pids.index(pid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Pos: " + str(pos))
		status = gamedict[listing][pos][1]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " listing: " + str(gamedict[listing][pos]))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Status: " + status)

		# Step 1.1 - Check if player is changing their fixed/unfixed status
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1.1 - Check if player is changing their fixed/unfixed status")
		if status != fixed: # Changing fixed to unfixed, or unfixed to fixed
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Current status and requested status are different")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if message author has permission to change status to from unfixed to fixed")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " listing: " + str(listing))
			if pid == str(ctx.message.author.id) and status == "fixed":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is making themselves unfixed. Authority ok")
			elif fixedauth == False:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority not allowed")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
				return (ctx, memberobj.mention + " You do not have authority to change status to fixed")
			gamedict[listing][pos] = (pid, fixed)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating game embeds")
			guildid  = ServData["GuildID"]
			guildobj = ctx.bot.get_guild(int(guildid))
			try:
				await UpdateGameEmbedsBot(ctx.bot, ServData, guildobj, gameid, tabs=tabs)
			except:
				logger.warning(tb(tabs) + "Couldn't find a guild with id " + str(guildid) + " in ListPlayer for some reason?\n" + PrintException())
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, "The " + listing + " status for player " + memberobj.mention + " in game " + gameid + " has been changed from " + status + " to " + fixed)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Already in list but not updating status. ")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " is already in the " + listing + " for game " + gameid + " (" + status + ")" )
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1 Passed")
	
	# Step 2 - Check if player is in other listing and fixed
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2 - Check if player is in other listing and fixed")
	otherlistpos = None
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Other list: " + str(gamedict[other]))
	pids = [pl[0] for pl in gamedict[other]]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pids: " + str(pids))
	if pid in pids:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is in " + other + " list")
		otherlistpos = pids.index(pid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Pos: " + str(otherlistpos))
		status = gamedict[other][otherlistpos][1]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Status: " + status)

		# Step 2.1 - Check if player is fixed in other
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2.1 - Check if player is fixed in other status")
		if status == "fixed" and fixed == "unfixed" and fixedauth == False:
			logger.debug(tb(tabs+2) + "Player is fixed")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " is listed as \"fixed\" for the " + other + " in game " + gameid + ". Can't add to " + listing + " until they are manually removed from the " + other)		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Member is not fixed")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2 Passed")
	
	# Step 3 - Check that player is of matching level
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 3 - Check that player is of matching level")
	if SS["settings"]["levelcapson"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting player's level from their nickname")
		theirnick = memberobj.nick
		if theirnick == None:
			theirnick = memberobj.display_name
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " theirnick: " + theirnick)	
		level = GetCharLevel(theirnick, tabs=tabs)
		if type(level) == type(""):
			logger.debug(tb(tabs) + str(level))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " " + str(level))
		
		if gamedict["minlevel"] in ["", " "] or gamedict["maxlevel"] in ["", " "]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Minlevel or maxlevel isn't set yet")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " Minlevel or maxlevel isn't set yet")
		
		if level < 	int(gamedict["minlevel"]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Character level " + str(level) + " is below minlevel " + str(gamedict["minlevel"]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " Character level " + str(level) + " is below minlevel " + str(gamedict["minlevel"]))		
	
		if level > 	int(gamedict["maxlevel"]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Character level " + str(level) + " is below maxlevel " + str(gamedict["maxlevel"]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " Character level " + str(level) + " is above maxlevel " + str(gamedict["maxlevel"]))
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " levelcapson is OFF")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 3 Passed")

	# Step 4 - Check that player isn't listed in too many games
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4 - Check that player isn't listed in too many games")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting list of future games")
	future = ServData["players"][str(memberobj.id)]['r']
	maxallowed = SS["settings"]["playermaxroster"]
	plural2 = "rostered" # for the output message below
	verb = "rostering"
	if listing == "sideline":
		maxallowed = SS["settings"]["playermaxsideline"]
		future = ServData["players"][str(memberobj.id)]['s']
		plural2 = "sidelined"
		verb = "sidelining"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Max allowed: " + maxallowed + ". Future games: " + str(future))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is in the " + listing + "for "  + str(len(future)) + " future games")
	if len(future) and int(maxallowed) >= 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking limit")
		if len(future) >= int(maxallowed):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Has too many future rostered games")
			plural = str(len(future)) + " game"			
			if len(future) > 1:
				plural += "s"
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
			return (ctx, memberobj.mention + " is already " + plural2 + "  for " + plural + "\nPlease unlist down to " + str(int(maxallowed)-1) + " game/s before " + verb + " for more")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is within limits")
		
		# Step 4.1: Check that player isn't playing more games in a row than playermaxconsecutive
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.1 - Check that player isn't listed in too many games")
		consec = SS["settings"]["playermaxconsecutive"]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Consecutive games is: " + consec)
		if int(consec) >= 0 and listing == "roster":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking consecutive games")
			conseccount = CheckConsecutiveRosters(ServData, str(memberobj.id), gameid)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Has " + str(consec) + " games rostered")
			if conseccount > int(consec):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has too many consecutive games lined up. Limit: " + consec)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
				return (ctx, memberobj.mention + " can't be listed for game " + gameid + " because the player will have played too many games in a row")		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4 Passed")
	
	# Step 5 - Check if there are empty spaces
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5 - Check if there are empty spaces")
	maxp = int(gamedict["maxplayers"])
	if listing == "sideline":
		maxp =  int(gamedict["maxsidelines"])
	listed = len(gamedict[listing])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Listed: " + str(listed) + ". Max Players: " + str(maxp))
	newpos = "end"
	if listed >= maxp:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There were no free spots")	
		
		# Step 5.05: Check if it's the roster and the player is being added as fixed, as will just increase the maxplayers
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5.05: Check if it's the roster and the player is being added as fixed, as will just increase the maxplayers")
		if listing == "roster" and fixed == "fixed" and fixedauth:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Just increasing roster size to fit")
			was = gamedict["maxplayers"]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " maxplayers was: " + was)
			gamedict["maxplayers"] = str(maxp + 1)
			now = gamedict["maxplayers"]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " maxplayers now: " + now)
			output = (chan, memberobj.mention + " Maxplayers for game " + gameid + " was " + was + " and is now " + now)
			outputlist.append(output)
			# Player will get their sidelines record updated in step 8
		else:
			# Step 5.1: Check if there is a lower priority listed player
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5.1 - Check if there is a lower priority player")
			thisp = CalcPlayerPriority(ServData, str(memberobj.id), tabs)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " This player's priority: " + str(thisp))
			higherp = []
			for pos, (pl, status) in enumerate(gamedict[listing]):
				pdata = (pos, pl, CalcPlayerPriority(ServData, pl, tabs))
				if pdata[2] > thisp and status != "fixed":
					higherp.append(pdata)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Worse priority players: " + str(higherp))
			
			if len(higherp) == 0 or SS["settings"]["prioritieson"] == "0":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No worse priority players and no room")
				msg = memberobj.mention + " unable to " + listing + " for game " + gameid + " because there are no unfixed players"
				if SS["settings"]["prioritieson"] == "0":
					msg += " of lower priority"
				output = (ctx,  msg)
				outputlist.append(output)
				if sendtosideline:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending this player to sidelines")
					output = await ListPlayer(ctx, ServData, SS, memberobj, gamedict, priv, listing="sideline", fixed=fixed, whisper=whisper, tabs=tabs)
					if type(output) == type([]):
						outputlist += output
					else:
						outputlist.append(output)
				elif otherlistpos != None:
					# Step 5.11 - removing from other list, if necessary
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5.11 - removing from other list, if necessary")
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing from other: " + other + " at pos " + str(otherlistpos))
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Entry in other: " + str(gamedict[other][otherlistpos]))
					if gamedict[other][otherlistpos][0] == pid:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing player")
						del gamedict[other][otherlistpos]
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Other list now: " + str(gamedict[other]))
						RemoveFromTeam(ServData, gameid, pid, other, removefixed=True, tabs=tabs)
						output = (chan, memberobj.mention + " was removed from " + listing + " to make the switch")
						outputlist.append(output)
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Other " + other + " list is now: " + str(gamedict[other]))	
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5.11 Complete")
				else:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not sending to sidelines")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputlist: " + str(outputlist))
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
				return outputlist
	
			# Step 5.2 - Sideline or remove lower priority player
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5.2 - Sideline or remove lower priority player")
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Lower priority player found. Getting their position")	
			higherp = sorted(higherp, key=lambda element: (element[2], element[0]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " List of players sorted by priority then position: " + str(higherp))
			newpos = higherp[-1][0]
			upid = higherp[-1][1]
			uprio = higherp[-1][2]
			ufixed = gamedict[listing][newpos][1]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player with worse priority (" + str(uprio) + ") is at roster position " + str(newpos) + ", id " + str(upid))
			if listing == "roster":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sidelining worse priority player " + str(upid))
				if gamedict["sidelineson"] == "1":
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding the player to the start of the sidelines")
					gamedict["sideline"].insert(0, (upid, ufixed))
	
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating demoted user's game lists")
					RemovePlayerGameList(ServData, upid, gameid, "r", tabs=tabs)
					AddPlayerGameList(ServData, upid, gameid, "s", tabs=tabs)
					
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting demoted from roster")
					del gamedict["roster"][newpos]
					
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting demoted user object")
					otherpobj = await ctx.bot.fetch_user(int(upid))
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Other player object: " + str(otherpobj))
					if otherpobj != None:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating demoted's output message")
						newoutput = otherpobj.mention + " has been removed from the roster for game " + gameid + " due to priorities"				
						output = (otherpobj, newoutput)
						outputlist.append(output)
				else:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No sidelines to demote player to")
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating demoted user's game lists")
					RemovePlayerGameList(ServData, upid, gameid, "r", tabs=tabs)				
					othermember = await ctx.bot.fetch_user(int(upid))
					if othermember != None:
						output = (othermember, othermember.mention + "You have been removed from the roster for game " + gameid + " as there are too many listed")
						outputlist.append(output)
			else:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing player from sideline as it has reached it's maximum")
				del gamedict[listing][newpos]
				othermember = await ctx.bot.fetch_user(int(upid))
				if othermember != None:
					output = (othermember, othermember.mention + "You have been removed from the sidelines for game " + gameid + " as there are too many listed")
					outputlist.append(output)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 5 Passed")
	
	# Step 6 - Add the player at the stored position
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 6 - Add the player at the stored position")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if user has authority to use fixed status")
	if fixed == "fixed":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Requesting fixed status")
		authname = "rosterfixed"
		if listing == "sideline":
			authname = "sidelinefixed"
		auth = SS["settings"]["authority"][authname]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority level is " + auth + " and priv is " + str(priv))
		if priv > int(auth):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority not allowed. Using unfixed")
			output = (chan, memberobj.mention + " You do not have authority to change status to fixed. Using unfixed")
			fixed = "unfixed"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority for status passed")
		
	#if newpos == "end":
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding the player straight to the end")
	gamedict[listing].append([pid, fixed])
	#else:
		#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Inserting player at position " + str(newpos))
		#gamedict[listing].insert(newpos, (pid, fixed))
	output = (chan, memberobj.mention + " has been added to the " + listing + " for game " + gameid)
	outputlist.append(output)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 6 Passed")
	logger.debug(tb(tabs) + listing + " is now: " + str(gamedict[listing]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output so far: ")
	for each in outputlist:
		logger.debug(tb(tabs+1) + str(each))

	# Step 7 - Updating the player's recorded listings
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 7 - Updating the player's recorded listings")
	letter = 'r'
	if listing == "sideline":
		letter = 's'
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's \"" + letter + "\" list was: " + str(ServData["players"][pid][letter]))
	if gameid not in ServData["players"][pid][letter]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding " + gameid + " to letter " + letter)
		ServData["players"][pid][letter].append(gameid)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's \"" + letter + "\" list is now: " + str(ServData["players"][pid][letter]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 7 Complete")
	
	# Step 8 - removing from other list, if necessary
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 8 - removing from other list, if necessary")
	if otherlistpos != None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing from other: " + other + " at pos " + str(otherlistpos))
		if gamedict[other][otherlistpos][0] == pid:
			del gamedict[other][otherlistpos]
			output = (chan, memberobj.mention + " was removed from " + other + " to make the switch")
			outputlist.append(output)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating player's roster/sideline record")
			RemoveFromTeam(ServData, gameid, pid, team=other, removefixed=True, tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Other " + other + " list is now: " + str(gamedict[other]))	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output so far: ")
	for each in outputlist:
		logger.debug(tb(tabs+1) + str(each))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 8 Complete")
	
	# Step 9 - Sending Updates
	logger.debug(tb(tabs+1) + "Step 9 - Sending Updates")
	author = None
	aid	   = None
	if type(ctx) == type(ext.commands.Context):
		author = ctx.message.author
		aid    = author.id
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " author: " + str(author))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Prepping a message for the author for each message created so far that wasn't for them")
	ocopy = outputlist[:]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ocopy: " + str(ocopy))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ctx.message.author: " + str(author))
	for each in ocopy:
		logger.debug(tb(tabs+1) + "This message: " + str(each))
		if each[0] == author or each[0] == ctx: # Don't repeat output to ctx from above, such as for ListMe
			logger.debug(tb(tabs+2) + "Not adding: same recipient")
		else:
			logger.debug(tb(tabs+2) + "New message. Adding")
			outputlist.append((ctx, each[1]))			
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output before adding others that should be alerted: " + str(outputlist))
	msg = {"serverdata": ServData, "ctx": ctx, "guild": ctx.guild, 	"ss": ServData, "ac": Commands.AC, "author":ctx.author,"uargs":[],"numargs":0,"authority":priv}
	users = CollateUpdateMsgs(msg, gameid, group=listing, tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Users: " + str([u.name for u in users]))
	for player in users:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking " + str(player.name) + ", obj: " + str(player))
		tabs+=1
		if player.id != aid and player.id != memberobj.id and player.bot == False:	# Don't notify the person that got 		
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending to them")
			ocopy = outputlist[:]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ocopy: " + str(ocopy))
			for each in ocopy:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " This message: " + str(each))
				if each[0] == player: # Don't repeat output to ctx
					logger.debug('\t\t\t\t\t' + "Message will already be sent to this person. Not adding")
				else:
					logger.debug('\t\t\t\t\t' + "Person hasn't received this message so far. Adding")
					outputlist.append((player, each[1]))					
		else:
			logger.debug(tb(tabs+2) + "Skipping as is the message sender, the whispered member, or a bot")
		tabs-=1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished Sending Updates")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output at the end: ")
	for each in outputlist:
		logger.debug(tb(tabs+1) + str(each))	

	if gamedict["published"] == "1":
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ListPlayer")
	return outputlist

async def UnlistPlayer(ctx, ServData, SS, memberobj, gamedict, priv, unlisting="both", whisper=False, movefixed=False, tabs=0):
	""" Unlisting a player a game roster and sideline """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UnlistPlayer")
	tabs += 1
	logger.debug(tb(tabs+1) + "Data received:")
	for each in [("ctx", ctx), ("member", memberobj), ("member.id", str(memberobj.id)), ("gamedict", gamedict), ("unlisting", unlisting), ("whisper", whisper)]:
		logger.debug(tb(tabs+1) + each[0] + ": " + str(each[1]))

	gameid  	= gamedict["id"]
	pid			= str(memberobj.id)
	outputlist	= []
	chan 		= ctx
	if whisper and not memberobj.bot: #whisper means "whisper updates"
		chan = memberobj		
	
	author = None
	aid	   = None
	if type(ctx) == type(ext.commands.Context):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output channel is a context rather than a user")
		author = ctx.message.author
		aid    = author.id
		if author == memberobj: # Can remove self from any list (whether listme or sunlist)
			movefixed = True
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output channel is a a user")
	logger.debug(tb(tabs+1) + "author: " + str(author))
	
	group = {"both": ["roster", "sideline"],
			 "roster": ["roster",],
			 "sideline": ["sideline",]}
	total = 0
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking each group in " + str(group[unlisting]))
	for each in group[unlisting]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking this one: " + str(each))
		tabs+=1
		logger.debug(tb(tabs) + each + " before: " + str(gamedict[each]))
		result = RemoveFromTeam(ServData, gameid, pid, each, movefixed, tabs=tabs)
		if result == -1:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Don't have authority to remove fixed players")
			outputlist.append((ctx, "You don't have authority to remove fixed players"))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of this one: " + str(each))
			continue
		total += int(result)
		if result:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player was removed from " + each)
			outputlist.append((ctx, ctx.message.author.mention + " Removed " + memberobj.mention + " from the " + each + " of game " + gameid))
		if result and each == "roster":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Promoting from Sidelines since a space was free")
			presult = await PromoteFromSidelines(ctx.bot, ServData, gameid, movefixed=False, tabs=tabs) #don't movefixed when someone was just being removed
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Promoted from sidelines: " + TOGGLEFT[presult])
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputlist so far: " + str(outputlist))
		logger.debug(tb(tabs) + each + " after: " + str(gamedict[each]))
		if result:
			#  Sending Updates
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending Updates")
			# Prep a message for the author for each message created so far
			ocopy = outputlist[:]
			logger.debug(tb(tabs+2) + "ocopy: " + str(ocopy))
			logger.debug(tb(tabs+2) + "ctx.message.author: " + str(author))
			for num, mess in enumerate(ocopy):
				logger.debug(tb(tabs+3) + "This message: " + str(mess))			
				if type(mess) == type(bool):
					logger.debug(tb(tabs+4) + "I can't figure out how a bool got in here")
					outputlist[num] = (ctx, "") # this removes the boolean without disturbing the list order and won't output a message
				if mess[0] == author or mess[0] == ctx: # Don't repeat output to ctx from above, such as for ListMe
					logger.debug(tb(tabs+4) + "Not adding: same recipient")
				else:
					logger.debug(tb(tabs+4) + "New message. Adding")
					outputlist.append((ctx, mess[1]))	
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output before adding others that should be alerted: " + str(outputlist))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending each update now")
			msg = {"serverdata": ServData, "ctx": ctx, "guild": ctx.guild, 	"ss": ServData, "ac": Commands.AC, "author":ctx.author,"uargs":[],"numargs":0,"authority":priv}
			users = CollateUpdateMsgs(msg, gameid, group=unlisting, tabs=tabs)
			for player in users:
				logger.debug(tb(tabs+1) + "Checking " + str(player.nickname))
				tabs+=1
				if player.id != aid and player.id != memberobj.id and player.bot == False:	
					logger.debug(tb(tabs+2) + "Sending")
					ocopy = outputlist[:]
					logger.debug(tb(tabs+2) + "ocopy: " + str(ocopy))
					for mess in ocopy:
						logger.debug(tb(tabs+3) + "This message: " + str(mess))
						if mess[0] == player: # Don't repeat output to ctx
							logger.debug(tb(tabs+4) + "Message will already be sent to this person. Not adding")
						if mess[1] == "":
							logger.debug(tb(tabs+4) + "A boolean got in somehow. Skipping")
						else:
							logger.debug(tb(tabs+4) + "Person hasn't received this message so far. Adding")
							outputlist.append((player, mess[1]))	
				else:
					logger.debug(tb(tabs+2) + "Skipping as is the message sender, the whispered member, or a bot")
				tabs-=1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished Sending Updates")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output at the end: ")
			for mess in outputlist:
				logger.debug(tb(tabs+1) + str(mess))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of this one: " + str(each))
		tabs-=1

	if total:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating embeds " + str(each))
		if gamedict["published"] == "1":
			await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	if total == 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No deletions made")
		output = (ctx, ctx.message.author.mention + " No roster/sideline listing found for game " + gameid)
		outputlist.append(output)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output at the VERY end: ")
	for mess in outputlist:
		logger.debug(tb(tabs) + str(mess))		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UnlistPlayer")		
	return outputlist	
	
# ~~~~~~~~~~~~~~~~~~~~~~~~ Commands for GMs to make and edit games

def NewGameHelp(msg, tabs=0):
	""" Prints Help on making a new game """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of NewGameHelp")
	tabs += 1
	
	ctx 		= msg["ctx"]			# the context bot thing
	uargs 		= msg["uargs"]			# the words given by the author
	command = uargs[0]
	args = len(uargs)
	
	output = "Use the following command to create a new game:\n"
	output +="!rb newgame <timezone> <year> <month> <day> <24hour:min>\n"
	output += "For example: !rb newgame America/Phoenix 2020 04 25 23:10\n"
	output += "\t!rb alltimezones to see the list of timezones you can use\n"
	output += "\t!rb mytimezone to set yours\n\n"
	output += "Once created, you will be told the Game ID you need to use to set the variables:\n"
	output += "!rb <Game ID> <variable name> <new variable>\n\n"
	output += "These are the variables you can use:"
	for each in Game.data.keys():
		if each not in ["roster", "sideline", "image", "publishid", "tier", "reminders"]:
			output += "\n\t" + each
	output += "\n\n!rb for more info and the readme"
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of MakeNewGame")
	return (ctx, output)

def MakeNewGame(msg, tabs=0):
	""" Creates a newgame with the given time data, or returns Help on making a new game """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of MakeNewGame")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	outputtup = (ctx, "")

	# check authority level
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
	Authorised = AuthorityCheck(SS, authorobj, "newgame", priv, command, tabs=tabs)
	if Authorised[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
		outputtup = (ctx, Authorised[1])
		return outputtup
	
	# Check if asking for newgame help
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if asking for newgame help")
	if args > 1 and uargs[1].lower() in ["help", "?"]:
		return NewGameHelp(msg, tabs=tabs)
	
	times = ["timezone", "year", "month", "day", "24hour:minute"]
	gm = authorobj
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking arguments given")
	error = "Time must be in large to small format: " + " ".join(times[:4]) + " " + times[-1] + ". For example: America/Phoenix 2020 04 25 23:10\nType !rb alltimezones to see the list of timezones you can use and !rb mytimezone to set yours"
	tz = None
	if args == 1:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No args given. Returning New Game Help")
		return NewGameHelp(msg, tabs=tabs)
	elif args == 2 and uargs[1] == "timezones":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Printing timezones")
		return PrintTimezones(msg, tabs=tabs)
	elif "etc/gmt" in uargs[1].lower():
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not using etc/gmt")
		return (ctx, authorobj.mention + " Please use !rb alltimezones to check what timezones you can use")
	elif args == 5 and uargs[1] not in pytz.all_timezones:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Using player's own timezone")
		pid = str(authorobj.id)
		ptz = Serv["players"][pid]["tz"]
		if ptz not in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has set tz to " + ptz)
			tz = ptz
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many or too few arguments given")
			return (ctx, error)
	elif uargs[1] in pytz.all_timezones and args != 6:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many or too few arguments given")
		return (ctx, error)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wrong arguments given")
		return (ctx, error)		
		
	hm = uargs[-1]
	d = uargs[-2]
	mo = uargs[-3]
	y = uargs[-4]
	if tz == None:
		tz = uargs[-5]
	
	dt = y + " " + mo + " " + d + " " + hm
	
	logger.debug(tb(tabs) + tz + " " + dt)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting the given text: " + " ".join(uargs[2:]))
	converted = ConvertTimezone(tz, dt, "UTC", tabs=tabs)
	if type(converted) != type(""):
		return (ctx, authorobj.mention + " That timezone makes no sense!\n" + str(converted) + "\n Check the timezones list and formatting and try again\n" + error)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Conversion ok. Creating game object")
	
	gameid = CreateGameID(converted, ctx.message.author.display_name, tabs=tabs)
	copyid = "default"
	if "oldgid" in msg.keys():
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating a game from " + msg["oldgid"])	
		copyid = msg["oldgid"]
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating a game from default")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating new Game object")	
	thisgame = Game(Serv, guildobj.id, dt, tz, str(authorobj.id), gameid, copyid, tabs=tabs)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game created!")
	logger.debug(tb(tabs) + str(thisgame.data.items()))
	
	while gameid in Serv["games"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Gameid " + gameid + " already existed.")
		if "." in gameid: # decimal already added, so increment it
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Incrementing decimal value")
			num = int(gameid[-1])
			num = str(num+1)
			num = num[-1] # make sure it doesn't become double digits
			gameid = gameid[:-1] + num
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Gameid now " + gameid)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding decimal value")
			gameid += ".1"
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Gameid now " + gameid)
		thisgame.data["id"] = gameid
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Copying game object data to server game dict")
	Serv["games"][gameid] = thisgame.data
	logger.debug(tb(tabs) + str(Serv["games"].keys()))

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if date is past the deletion timeframe")
	past = CheckAgeOfCompleted(Serv, gameid, thisgame, tabs)
	outputmsg = ""
	if past:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is old and will be deleting. Warning player")
		outputmsg = "***WARNING!***\n You have used a game date over " + str(DELETECOMPLETEDGAMES) + " days. This game will be automatically deleted soon. Please check your date!\n\n"
	
	helper = NewgameChainCommands(ctx.bot, Serv, gameid, tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of MakeNewGame")
	return (ctx, outputmsg + authorobj.mention + " Game created!\n Your GameID is " + gameid + "\n!rb " + gameid + " <subcommand> to modify and publish\n" + helper)

async def GSGameData(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of GSGameData")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	numargs 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid		= uargs[1]
	subc 		= None
		
	if numargs == 2:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting all game data")
				
		# check if it's the Server Default game or not
		req = "viewgame"
		if gameid.lower() == "default":
			req = "default"
		
		# check authority level
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
		Authorised = AuthorityCheck(SS, authorobj, req, priv, command, tabs)
		if Authorised[0] == False:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
			outputtup = (ctx, Authorised[1])
			return outputtup
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
			
		outputtup = PrintGameInfo(msg)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSGameData")
		logger.debug('\t' + "Output is: " + str(outputtup))
		return outputtup
		
	if numargs >= 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting or Setting specific game data")
		uargs[2] = uargs[2].lower()
		subc = uargs[2]		
		
		# check if it's the Server Default game or not
		req = "gameid"
		if gameid.lower() == "default":
			req = "default"	

		# check authority level
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
		Authorised = AuthorityCheck(SS, authorobj, req, priv, command, subc=subc, gamedict=Serv["games"][gameid], tabs=tabs)
		if Authorised[0] == False:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
			outputtup = (ctx, Authorised[1])
			return outputtup
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
		
		# Check if gmsonlyeditown is set to true and test
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gmsonlyeditown Check")
		if SS["settings"]["gmsonlyeditown"] == "1" and priv != 1 and str(authorobj.id) != Serv["games"][gameid]["gm"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass gmsonlyeditown Check")
			outputtup = (ctx, authorobj.mention + " Based on a server setting, you cannot edit the game of another GM")
			return outputtup

		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if just asking for help")
		if uargs[2].lower() in ["help", "?"]:
			helpmsg = NewGameHelp(msg)[1]
			if gameid != "default":
				helpmsg += "\n" + NewgameChainCommands(ctx.bot, Serv, gameid, tabs)
			outputtup = (ctx, helpmsg)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " subc is " + subc)
			if subc.lower() not in AC["gameid"]:			
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No game variable matches " + subc)
				outputtup = (ctx, "No game variable matches " + subc)
			elif asyncio.iscoroutinefunction(AC["gameid"][subc]):
				outputtup = await AC["gameid"][subc](msg, tabs)
			else:
				outputtup = AC["gameid"][subc](msg, tabs) # Call the GetSet Function
			
			# Add helper message
			if Serv["games"][gameid]["published"] == "0" and subc not in ["listme", "unlistme", "rosterme", "unrosterme", "sidelineme", "unsidelineme", "roster", "sideline"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding helper output")
				helper = NewgameChainCommands(ctx.bot, Serv, gameid, tabs)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " helper: " + str(helper))
				#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Printing embed") # Not gonna add this. Peeps can just call !rb <gameid> when they want to see it
				#newembed = GetGameInfoEmbed(ctx.bot, Serv, gameid, Serv["games"][gameid]["timezone"], tabs=0)
				#await ctx.send(embed=newembed)
				if type(outputtup) == type(()):				
					if outputtup[1] == "List of outputups":
						thistup = (ctx, helper)
						outputtup[2].append(thistup)
					else:
						outputtup = (outputtup[0], str(outputtup[1]) + "\n" + str(helper))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSGameData")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
		return outputtup	

def GameCopy(msg, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of GameCopy")
	tabs += 1

	# Easy access variables
	ctx 		= msg["ctx"]
	SS 			= msg["ss"]	
	guildobj 	= msg["guild"]
	authorobj	= msg["author"]
	serverdata 	= msg["serverdata"]
	uargs 		= msg["uargs"]
	numargs		= msg["numargs"]
	AC 			= msg["ac"]
	priv 		= msg["authority"]		# int for the author's authority level
	outputtup 	= (ctx, "")
	command 	= uargs[0]
	
	# check authority level
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
	Authorised = AuthorityCheck(SS, authorobj, "copy", priv, command)
	if Authorised[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
		outputtup = (ctx, Authorised[1])
		return outputtup
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
		
	# check that the given game exists
	if numargs >= 2:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking given game exists")
		oldgid = uargs[1]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Old game id: " + oldgid)
		
		if oldgid not in serverdata["games"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching game found")
			outputtup = (ctx, authorobj.mention + " No matching game found for " + oldgid)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " oldgid found")
			msg["oldgid"] = oldgid
			msg["uargs"].pop(0)
			msg["uargs"][0] = "newgame"
			msg["numargs"] = len(msg["uargs"])
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " New uargs for the Newgame function: " + str(msg["uargs"]))
			# Making the NewGame
			outputtup = MakeNewGame(msg)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only given !rb copy. Output help info")
		outputtup = (ctx, authorobj.mention + " provide an existing game id and the timezone and date/time info to create a copy of that game")
			
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameCopy")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(outputtup))
	return outputtup

async def GameUpdateEmbeds(msg, tabs=0):
	""" Allows GMs to force published embeds to be updated """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GameUpdateEmbeds")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"][gameid]	
	
	auth = AuthorityCheck(SS, authorobj, "gameid", priv, "gameid", subc="update", gamedict=GameDict, tabs=tabs)
	if auth[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not authorised")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameUpdateEmbeds")
		return auth
	
	result = None
	if GameDict["published"] == "1" and GameDict["completed"] == "0":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating")
		num = await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
		result = (ctx, authorobj.mention + " Forced update of " + str(num) + " published embeds")
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is completed or isn't published to update the embeds for")
		result = (ctx, authorobj.mention + " Game " + gameid + " is either completed or not published. No embeds to update.")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameUpdateEmbeds")
	return result	

async def GameAudit(msg, tabs=0):
	""" Allows GMs to force game roster to be audited """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GameAudit")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"][gameid]	
	
	auth = AuthorityCheck(SS, authorobj, "gameid", priv, "gameid", subc="audit", gamedict=GameDict, tabs=tabs)
	if auth[0] == False:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not authorised")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameAudit")
		return auth
	
	await AuditRoster(ctx.bot, Serv, gameid, movefixed=False, tabs=tabs)

	result = (ctx, authorobj.mention + " Forced Audit of Game " + gameid + " complete")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameAudit")
	return result	
	
# ~~~ Requires Discord IDs

def GSserver(msg, tabs=0):
	""" Returns the Server of the selected game (can't be set) """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS server")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict = Serv["games"]
	
	# Get
	server = utils.get(ctx.bot.guilds, id=GameDict[gameid][subc])
	name = server.name
	
	# No Set
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning Server Name: " + name)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSserver")
	return (ctx, authorobj.mention + " The Guild for Game " + gameid + " is " + name)

async def GSgm(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS gm")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GMid = GameDict[gameid]["gm"]
	member = utils.get(ctx.message.guild.members, id=int(current))
	if member == None:
		dname = current + " (left)"
	else:
		dname = member.display_name
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Current GM is " + dname)
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + dname)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgm")
		return (ctx, authorobj.mention + " The GM for game " + gameid + " is " + dname)	
	
	# Set
	
	# Check for mentions
	member2 = None
	
	if len(ctx.message.mentions):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Found a member mentioned")
		member2 = ctx.message.mentions[0]
	else:
		newgm = uargs[3]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No members mentioned. Checking by name")
		# Check that such a member exists in this guild
		member2 = utils.get(guildobj.members, display_name=newgm)
	
	if member2 == None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No such member \"" + uargs[3] + "\" found")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgm")
		return (ctx, authorobj.mention + " No such member \"" + uargs[3] + "\" could be found")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " New GM is " + str(member2))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	GameDict[gameid]["gm"] = str(member2.id)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating Player Priority data for rostered games, etc")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " previous gm: " + str(current))
	pl = Serv["players"][str(current)]
	while gameid in pl["gp"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing from gp")
		pl["gp"].remove(gameid)
	while gameid in pl["gr"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing from gr")
		pl["gr"].remove(gameid)
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " next gm")	
	pl = Serv["players"][GameDict[gameid]["gm"]]
	if GameDict[gameid]["completed"] == "1" and gameid not in pl["gp"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding to gp")
		pl["gp"].append(gameid)
	if GameDict[gameid]["completed"] == "0" and gameid not in pl["gr"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding to gr")
		pl["gr"].append(gameid)
		
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + member.mention + ", and is now " + member2.mention
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + member.display_name + " and is now " + member2.display_name
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgm")
	return outputtup

async def GStextchannel(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GStextchannel")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]

	# Check for aliases 
	if subc.lower() in ["tc", "text"]: 
		uargs[2] 		= "textchannel"
		subc 			= uargs[2]
		msg["uargs"] 	= uargs

	current 	= GameDict[gameid][subc]
	chan 		= utils.get(ctx.message.guild.channels, id=current)
		
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + str(chan)) # type cast to str in case a channel hasn't been set
		message = authorobj.mention + " The text channel for game " + gameid + " is unset"
		if chan != None:
			message = authorobj.mention + " The text channel for game " + gameid + " is " + chan.mention
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSname")
		return (ctx, message)
	
	# Make sure given value is valid
	chan = uargs[3].lower()
	if len(ctx.message.channel_mentions):
		chan = ctx.message.channel_mentions[0]
	else:
		chan = utils.get(ctx.message.guild.channels, name=uargs[3].lower())
	
	if chan == None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No channel found")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSname")
		return (ctx, authorobj.mention + " No matching channel found")
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	GameDict[gameid][subc] = str(chan.id)

	result = authorobj.mention + " The text channel for game " + gameid + " is now " + chan.mention
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " is now #" + chan.name
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStextchannel")
	return outputtup

async def GSvoicechannel(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSvoicechannel")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	
	
	# Check for aliases 
	if subc.lower() in ["vc", "voice"]:
		logger.debug(tb(tabs) + "Switching vc or voice for voicechannel")
		uargs[2] 		= "voicechannel"
		subc 			= uargs[2]
		msg["uargs"]	= uargs
	
	current 	= GameDict[gameid][subc]
	logger.debug(tb(tabs) + "Current channel is " + str(current))
		
	logger.debug(tb(tabs) + "Getting currently set channel object")
	chan = utils.get(ctx.message.guild.channels, id=current)
	logger.debug(tb(tabs) + "Got chan " + str(chan))
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + str(chan)) # type cast to str in case a channel hasn't been set
		message = authorobj.mention + " The voice channel for game " + gameid + " is unset"
		if chan != None:
			message = authorobj.mention + " The voice channel for game " + gameid + " is " + chan.mention
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSvoicechannel")
		return (ctx, message)
	
	logger.debug(tb(tabs) + "Setting new voice channel")	

	# Make sure given value is valid
	logger.debug(tb(tabs) + "Getting given channel name")
	chan = " ".join(uargs[3:]).lower()
	logger.debug(tb(tabs) + "Given " + str(chan))
	chanlist = [c for c in guildobj.channels if c.name.lower() == chan and c.type == ChannelType.voice]
	logger.info('\t\t' + "Finding a voice channel in " + str([(c.id, c.name) for c in chanlist]))
	chan = None
	if len(chanlist):
		chan = chanlist[0]
	
	chanid = ""
	chanstr = ""
	result = ""
	if chan == None:
		logger.debug(tb(tabs+1) + "No channel found")
		chanid = ""
		chanstr = "None"
		result = "No channel could be found for that. Setting to None for now"
	else:
		logger.debug(tb(tabs+1) + "Found channel " + chan.mention + " " + str(chan.id))
		chanid = chan.id
		chanstr = chan.mention
	
	# Set
	logger.debug(tb(tabs+1) + "Setting new var")
	GameDict[gameid][subc] = str(chanid)

	result += authorobj.mention + " The voice channel for game " + gameid + " is now " + chanstr
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs+1) + "Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " is now " + chanstr
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs+1) + "No updates required")	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSvoicechannel")
	return outputtup

async def GSpublishchannels(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSpublishchannels")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	chans 		= []
	for chan in current:
		thischan = utils.get(ctx.message.guild.channels, id=int(chan))
		chans.append(thischan.mention)

	# Check for aliases 
	if subc.lower() in ["pc", ]: 
		uargs[2] = "publishchannels"
		subc = uargs[2]
		msg["uargs"] = uargs
		
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + " ".join(chans)) # type cast to str in case a channel hasn't been set
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublishchannels")
		return (ctx, authorobj.mention + " The publish channel/s for game " + gameid + ": " + " ".join(chans))
	
	# Make sure given value is valid
	chan = uargs[3].lower()
	if len(ctx.message.channel_mentions):
		chan = ctx.message.channel_mentions[0]
	else:
		chan = utils.get(ctx.message.guild.channels, name=uargs[3].lower())
	
	if chan == None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No channel found")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSname")
		return (ctx, authorobj.mention + " No matching channel found")
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if adding a new one or removing one")
	if str(chan.id) not in GameDict[gameid][subc]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not in current list. Adding and updating game embeds")
		GameDict[gameid][subc].append(str(chan.id))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " List is now: " + str(GameDict[gameid][subc]))
		message = authorobj.mention + " Added " + uargs[3] + " to publish channels"
		if GameDict[gameid]["published"] == "1":
			await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
			message += " and sent an embed to it"
		return (ctx, message) 
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing from current list")
	while str(chan.id) in GameDict[gameid][subc]:
		GameDict[gameid][subc].remove(str(chan.id))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " List is now: " + str(GameDict[gameid][subc])) 

	result = authorobj.mention + " Removed channel " + chan.mention + " from the publishchannels of game " + gameid
	result += "\nNote: This has not deleted the embed from that channel"
	outputtup = (ctx, result)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublishchannels")
	return outputtup

async def GSimage(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSimage")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"][gameid]
	current 	= GameDict[subc]

	# Get
	if args == 3 and len(ctx.message.attachments) == 0:	
		infobox = authorobj.name + " The image for game "  + gameid + " is not set"			
		if GameDict["image"] not in ["", None, "None", "none", "NONE"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating an embed for the image")
			infobox = Embed()
			infobox.title = authorobj.mention + " The image for game " + gameid + " is:"
			infobox.set_image(url=GameDict["image"])
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSimage")
		return (ctx,  infobox)

	if args > 3 and uargs[3].lower() in ["none", "blank", "remove", "empty", "delete"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing current image")
		GameDict["image"] = ""
		return (ctx, authorobj.mention + " Current image for game " + gameid + " was removed")
	
	# Set
	if len(ctx.message.attachments):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting image from an attachment")
		att = ctx.message.attachments[0]
		furl = att.url
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting image from an given url")
		furl = uargs[3]
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set image as " + str(furl))	
	GameDict[subc] = furl
	
	# Updates	
	if GameDict["completed"] == "0" and GameDict["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " is now " + chanstr
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")	
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating an embed for the image for output")
	infobox = Embed()
	infobox.title = authorobj.name + " The image for game " + gameid + " is now:"
	infobox.set_image(url=GameDict["image"])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSimage")
	return (ctx, infobox)

async def GSCompletedchannels(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSCompletedchannels")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	chans 		= []
	for chan in current:
		thischan = utils.get(ctx.message.guild.channels, id=int(chan))
		chans.append(thischan.mention)

	# # Check for aliases 
	# if subc.lower() in ["pc", ]: 
	# 	uargs[2] = "publishchannels"
	# 	subc = uargs[2]
	# 	msg["uargs"] = uargs
		
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + " ".join(chans)) # type cast to str in case a channel hasn't been set
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSCompletedchannels")
		return (ctx, authorobj.mention + " The publish channel/s for game " + gameid + ": " + " ".join(chans))
	
	# Make sure given value is valid
	chan = uargs[3].lower()
	if len(ctx.message.channel_mentions):
		chan = ctx.message.channel_mentions[0] # only grabbing the first one
	elif chan in ["clear", "del", "delete", "none", "empty"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Clearing channels")
		GameDict[gameid][subc] = []
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSCompletedchannels")	
		return (ctx, authorobj.mention + " Clearing completedchannels")
	else:
		chan = utils.get(ctx.message.guild.channels, name=uargs[3].lower())
	
	if chan == None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No channel found")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSCompletedchannels")
		return (ctx, authorobj.mention + " No matching channel found")

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if adding a new one or removing one")
	if str(chan.id) not in GameDict[gameid][subc]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Not in current list. Adding and updating game embeds")
		GameDict[gameid][subc].append(str(chan.id))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " List is now: " + str(GameDict[gameid][subc]))
		message = authorobj.mention + " Added " + uargs[3] + " to completedchannels"
		if GameDict[gameid]["completed"] == "1":
			await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
			message += " and sent an embed to it"
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSCompletedchannels")
		return (ctx, message) 
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing from current list")
	while str(chan.id) in GameDict[gameid][subc]:
		GameDict[gameid][subc].remove(str(chan.id))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " List is now: " + str(GameDict[gameid][subc])) 

	result = authorobj.mention + " Removed channel " + chan.mention + " from the completedchannels of game " + gameid
	result += "\nNote: This has not deleted the embed from that channel"
	outputtup = (ctx, result)

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSCompletedchannels")
	return outputtup

# ~~~ Roster Editing ~~~~

async def GSroster(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSroster")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	maxp = GameDict[gameid]["maxplayers"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting value")
		result = "The roster for game " + gameid + " is (max " + str(maxp) + " players):"
		if len(current):
			for num, (pid, fixed) in enumerate(current):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " num " + str(num) + ", pid " + str(pid) + ", fixed " +  fixed)
				member = utils.get(ctx.message.guild.members, id=int(pid))
				mname = ""
				if member == None:
					mname = pid + " (left)"
				else:
					mname = member.display_name
				result += "\n" + str(num+1) + ". " + mname + " (" + fixed + ")"
		else:
			result += "\n - No players yet"
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSroster")
		return (ctx, result)
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting value")
	outputlist = await AddToTeam(msg, tabs=tabs)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSroster")
	return outputlist

async def GSsideline(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSsideline")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	maxp = GameDict[gameid]["maxsidelines"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting value")
		result = "The sideline for game " + gameid + " is (max " + str(maxp) + " players):"
		if len(current):
			for num, (pid, fixed) in enumerate(current):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " num " + str(num) + ", pid " + str(pid) + ", fixed " + fixed)
				member = utils.get(ctx.message.guild.members, id=int(pid))
				mname = ""
				if member == None:
					mname = pid + " (left)"
				else:
					mname = member.display_name
				result += "\n" + str(num+1) + ". " + mname + " (" + fixed + ")"
		else:
			result += "\n - No players yet"
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsideline")
		return (ctx, result)

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	outputlist = await AddToTeam(msg)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsideline")
	return outputlist

async def AddToTeam(msg, tabs=0):
	""" Listing another player for a game by list, roster or sideline """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of AddToTeam")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]				# "game" command
	gameid		= uargs[1]
	listing		= uargs[2].lower()
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " uargs: " + str(uargs))
	if listing == "list":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Changing list to both")
		listing = "both"
	
	gamedict = Serv["games"][gameid]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if a player was mentioned")
	players = ctx.message.mentions
	if len(players) == 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No players mentioned")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of SList")
		return (ctx, authorobj.mention + " Can't list for game " + gameid + " as no player was mentioned")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority")
	status = "unfixed"
	outputlist = []
	if args > 4 and "fixed" in uargs:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Used fixed command")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " priv: " + str(priv))
		authname = "rosterfixed"
		adj = "rostered"
		if listing == "sideline":
			authname = "sidelinefixed"
			adj = "sidelined"
		logger.debug(tb(tabs) + str(authname)+ ": " + SS["settings"]["authority"][authname])		
		if priv > int(SS["settings"]["authority"][authname]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " User doesn't have permission to set " + adj + " status to fixed")
			output = (ctx, authorobj.mention + " You don't have permission to roster players as \"fixed\". Listing as unfixed")
			outputlist.append(output)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Status set to fixed")
			status = "fixed"

	plist = []
	for each in players:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Collating player: " + str(each))
		pid = str(each.id)
		plist.append((CalcPlayerPriority(Serv,pid, tabs=tabs), pid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sorting list")
	plist = sorted(plist, key=lambda element: (element[0], element[1]))
	for each in plist:
		memobj = await ctx.bot.fetch_user(int(each[1]))
		output = await ListPlayer(ctx, Serv, SS, memobj, gamedict, priv, listing=listing, fixed=status, whisper=True, tabs=tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output from ListPlayer: " + str(output))
		if type(output) == type([]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Joining lists")
			outputlist = outputlist + output
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Appending list")
			outputlist.append(output)		
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputlist: " + str(outputlist))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of AddToTeam")
	return (ctx, "List of outputups", outputlist)

async def Sunlist(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of Sunlist")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"][gameid]
	maxp 		= GameDict["maxplayers"]
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authorised use of fixed")
	outputlist = []
	
	movefixed = False
	if "fixed" in uargs:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " fixed found")
		authname = "rosterfixed"
		if subc == "unsideline":
			authname = "sidelinefixed"
		auth = Serv["settings"]["authority"][authname]
		if priv > int(auth):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority not matched. Movefixed will be false")
			outputlist.append(ctx, authorobj.mention + " You don't have the " + authname + " authority to use the \"fixed\" argument")
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
			movefixed = True
		
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting value")
	listing = "both"
	if subc == "unroster":
		listing = "roster"
	elif subc == "unsideline":
		listing = "sideline"
	if len(ctx.message.mentions):
		for each in ctx.message.mentions:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting pid: " + str(each.id))
			output = await UnlistPlayer(ctx, Serv, SS, each, GameDict, priv, unlisting=listing, whisper=True, movefixed=movefixed, tabs=tabs)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output from UnlistPlayer: " + str(output))
			if type(output) == type([]):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Joining lists")
				outputlist = outputlist + output
			else:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Appending list")
				outputlist.append(output)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting all or unguilded")
		thislist = GameDict["roster"] + GameDict["sideline"]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Thislist is: " + str(thislist))
		members = []
		nonmembers = []
		for each in thislist:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Getting player: " + str(each[0]))
			player = None
			tries = 0
			while player == None and tries < 3:
				if tries != 0:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Couldn't find a player, waiting 0.5 secs")
					time.sleep(0.5)
				player = GetMember(ctx, each[0], tabs=tabs+1)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player: " + str(player))
				tries += 1
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tries: " + str(tries))
			if player == None:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't find player with pid: " + str(pid))
				unfound = True
				nonmembers.append(player)	
			else:
				members.append(player)
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Members are: " + str(members))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Non-members are: " + str(nonmembers))
		
		if "all" in uargs and len(members):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting ALL")
			for each in members:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting pid: " + str(each.id))
				output = await UnlistPlayer(ctx, Serv, SS, each, GameDict, priv, unlisting=listing, whisper=True, movefixed=movefixed, tabs=tabs)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output from UnlistPlayer: " + str(output))
				if type(output) == type([]):
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Joining lists")
					outputlist = outputlist + output
				else:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Appending list")
					outputlist.append(output)			
		elif ("unguilded" in uargs or "nonmembers" in uargs or "non-members" in uargs) and len(nonmembers):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting nonmembers")
			for each in nonmembers:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unlisting pid: " + str(each.id))
				output = await UnlistPlayer(ctx, Serv, SS, each, GameDict, priv, unlisting=listing, whisper=True, movefixed=movefixed, tabs=tabs)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output from UnlistPlayer: " + str(output))
				if type(output) == type([]):
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Joining lists")
					outputlist = outputlist + output
				else:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Appending list")
					outputlist.append(output)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No players mentioned")
			return (ctx, authorobj.mention + " No players mentioned to remove")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Sunlist")
	return (ctx, "List of outputups", outputlist)
	
# ~~~ Strings

async def GSname(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS name")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	name = GameDict[gameid]["name"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning " + name)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSname")
		return (ctx, authorobj.mention + " The name for game " + gameid + " is " + name)		
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	givenname = " ".join(uargs[3:])	
	GameDict[gameid]["name"] = givenname[:100]

	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + name + ", and is now " + GameDict[gameid]["name"]
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + name + ", and is now " + GameDict[gameid]["name"]
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSname")
	return outputtup

async def GSdescription(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS description")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdescription")
		return (ctx, authorobj.mention + " The description for game " + gameid + " is \n" + current)
	
	# Make sure given value is valid	
	new = " ".join(uargs[3:])
	limit = 500
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	GameDict[gameid][subc] = new[:limit]
	
	result = authorobj.mention + " The description for game " + gameid + " was \n" + str(current) + "\n...and is now...\n" + new[:limit]
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The description for " + guildobj.name + " game " + gameid + " was \n" + str(current) + "\n...and is now...\n" + new[:limit]
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdescription")
	return outputtup

async def GSgpreward(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS gpreward")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgpreward")
		return (ctx, authorobj.mention + " The gpreward for game " + gameid + " is " + str(current))
	
	# Make sure given value is valid
	new = " ".join(uargs[3:])
	
	# Check the length
	limit = 20
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgpreward")
		return (ctx, authorobj.mention + " Limit your variable to under " + str(limit) + " characters")
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	GameDict[gameid][subc] = str(new)
	
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + str(current) + " and is now " + new
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + new
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSgpreward")
	return outputtup
	
async def GSxpreward(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS xpreward")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSxpreward")
		return (ctx, authorobj.mention + " The xpreward for game " + gameid + " is " + str(current))
	
	# Set	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = " ".join(uargs[3:])
	
	# Check the length
	limit = 20
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSxpreward")
		return (ctx, authorobj.mention + " Limit your variable to under " + str(limit) + " characters")
	
	GameDict[gameid][subc] = str(new)
	
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + str(current) + " and is now " + new
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + new
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSxpreward")
	return outputtup

async def GSduration(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS duration")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSduration")
		return (ctx, authorobj.mention + " The duration for game " + gameid + " is " + str(current))
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = " ".join(uargs[3:])
	# Check the length
	limit = 20
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSduration")
		return (ctx, authorobj.mention + " Limit your variable to under " + str(limit) + " characters")
	
	GameDict[gameid][subc] = new
	
	result = authorobj.mention + " The duration for game " + gameid + " was " + str(current) + " and is now " + str(new)
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The duration for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + str(new)
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSduration")
	return outputtup

def GStier(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS tier")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStier")
		return (ctx, authorobj.mention + " The tier for game " + gameid + " is " + str(current))
		
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	# Make sure given value is valid
	new = uargs[3]
	# Check the length
	limit = 20 
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStier")
		return (ctx, authorobj.mention + " Limit your variable to under " + str(limit) + " characters")
	
	GameDict[gameid][subc] = new
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStier")
	return (ctx, authorobj.mention + " The tier for game " + gameid + " was " + str(current) + " and is now " + str(new))

async def GSlink(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSlink")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSlink")
		return (ctx, authorobj.mention + " The link set for game " + gameid + " is " + str(current))
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = " ".join(uargs[3:])
	# Check the length
	limit = 100
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSlink")
		return (ctx, authorobj.mention + " Limit your link to under " + str(limit) + " characters")
	
	GameDict[gameid][subc] = new
	
	result = authorobj.mention + " The link set for game " + gameid + " was " + str(current) + " and is now " + str(new)
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The duration for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + str(new)
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSlink")
	return outputtup


# ~~~ Requires Time Conversions

async def GSdatetime(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS datetime")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]

	# Check for aliases 
	if subc.lower() in ["date", "time"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting aliases")
		uargs[2] = "datetime"
		subc = uargs[2]
		msg["uargs"] = uargs
	
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	ctz 	= GameDict[gameid]["timezone"]
	times = ["timezone", "year", "month", "day", "24hour:minute"]
	
	# Get
	if args == 3: # returns the game in it's own timezone
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if player has set a tz")
		pid = str(authorobj.id)
		ptz = Serv["players"][pid]["tz"]
		dt = None
		if ptz not in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has a timezone set. Using that")
			dt = GetGameDateTime(Serv, gameid, ptz, tabs=tabs)
			return (ctx, authorobj.mention + " The datetime for game " + gameid + " is " + dt)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has no timezone set. Using what was stored in the game")
			dt = ctz + " " + current
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdatetime")
		return (ctx, authorobj.mention + " The datetime for game " + gameid + " is " + dt)
	elif args == 4: # returns the game date time in the given timezone
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Using the given timezone")
		tz = uargs[3]
		converted = ConvertTimezone(ctz, current, tz, tabs=tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converted result: " + str(converted))
		if type(converted) != type(""):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Invalid timezone string given: " + uargs[3])
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdatetime")
			error = "Time must be in large to small format: " + " ".join(times[:4]) + " " + times[-1] + ". For example: America/Phoenix 2020 04 25 23:10\nType !roster timezones to see the list of timezones you can use"
			return (ctx, authorobj.mention + " That timezone makes no sense!\n" + str(converted) + "\n Check the timezones list and formatting and try again\n" + error)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdatetime")
			return (ctx, authorobj.mention + " The datetime for game " + gameid + " in " + tz + " time is " + converted)			
	
	# Setting
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = " ".join(uargs[4:])
	tz = uargs[3]
	if "etc/gmt" not in tz and tz not in pytz.all_timezones:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if player has set a tz")
		pid = str(authorobj.id)
		ptz = Serv["players"][pid]["tz"]
		dt = None
		if ptz not in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has a timezone set. Using that")
			tz = ptz
			new = " ".join(uargs[3:]) # fixing the date time string
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player has given a tz or formatting that won't work below")
			
	try: # Check that the given args can be turned into a time format
		obj = datetime.strptime(new, TFORMAT)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " obj: " + str(obj))
	except (Exception, DiscordException) as e:
		edata = PrintException()
		logger.error('\t' + "There was an error converting timestring " + new)
		logger.error('\t' + str(edata))
		error = "Time must be in large to small format: " + " ".join(times[:4]) + " " + times[-1] + ". For example: America/Phoenix 2020 04 25 23:10\nType !roster timezones to see the list of timezones you can use or use !rb mytimezone to set yours"
		return (ctx, error)
	
	# Set val
	GameDict[gameid][subc] = new
	GameDict[gameid]["timezone"] = tz

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if date is past the deletion timeframe")
	past = CheckAgeOfCompleted(Serv, gameid, GameDict[gameid], tabs)
	outputmsg = ""
	if past:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is old and will be deleting. Warning player")
		outputmsg = "***WARNING!***\n You have used a game date over " + str(DELETECOMPLETEDGAMES) + " days. This game will be automatically deleted soon. Please check your date!\n\n"
	
	result = outputmsg + authorobj.mention + " The datetime for game " + gameid + " was " + ctz + " " + str(current) + " and is now " + tz + " " + new
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The datetime for " + guildobj.name + " game " + gameid + " was " + ctz + " " + str(current) + " and is now " + tz + " " + new
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSdatetime")
	return outputtup

def GStimezone(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS timezone")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	cdt		= GameDict[gameid]["datetime"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStimezone")
		return (ctx, authorobj.mention + " The timezone for game " + gameid + " is " + current)
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	if "etc/gmt" in new.lower() or new not in pytz.all_timezones:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Invalid timezone given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStimezone")
		error = "Time must be in large to small format: " + " ".join(times[:4]) + " " + times[-1] + ". For example: America/Phoenix 2020 04 25 23:10\nType !roster timezones to see the list of timezones you can use"
		return (ctx, authorobj.mention + " That timezone makes no sense!\n" + str(converted) + "\n Check the timezones list and formatting and try again\n" + error)

	GameDict[gameid]["datetime"] = ConvertTimezone(current, GameDict[gameid]["datetime"], new)
	GameDict[gameid][subc] = new
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GStimezone")
	return (ctx, authorobj.mention + " The datetime for game " + gameid + " was " + current + " " + cdt + " and is now " + GameDict[gameid][subc] + " " + GameDict[gameid]["datetime"])

# ~~~ Ints

def GSsession(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS session#")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsession#")
		return (ctx, authorobj.mention + " The name for game " + gameid + " is " + current)
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = int(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(edata))
		return (ctx, "") 
		
	GameDict[gameid][subc] = str(new)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsession#")
	return (ctx, authorobj.mention + " The session number for game " + gameid + " was " + str(current) + " and is now " + str(new))

async def GSminplayers(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS minplayers")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminplayers")
		return (ctx, authorobj.mention + " The minplayers for game " + gameid + " is " + str(current))

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = int(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(edata))
		return (ctx, "") 
	
	if new < 0:
		new = "0"
	elif new > int(GameDict[gameid]["maxplayers"]):
		new = GameDict[gameid]["maxplayers"]
		
	GameDict[gameid][subc] = str(new)
	
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + str(current) + " and is now " + str(new)  + " (can't be higher than maxplayers)"
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + new
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminplayers")
	return outputtup

async def GSmaxplayers(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS maxplayers")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]

	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxplayers")
		return (ctx, authorobj.mention + " The maxplayers for game " + gameid + " is " + str(current))

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	intnew = StrToInt(new) # convert to int
	
	if intnew > 20:
		new = "20"
	elif intnew < int(GameDict[gameid]["minplayers"]):
		new = GameDict[gameid]["minplayers"]
		
	GameDict[gameid][subc] = new
	
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + current + " and is now " + new + " (can't be lower than minplayers)"
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " game " + gameid + " was " + current + " and is now " + new
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxplayers")
	return outputtup

def GSmaxsidelines(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS maxsidelines")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxsidelines")
		return (ctx, authorobj.mention + " The maxsidelines for game " + gameid + " is " + str(current))
		
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var with: " + uargs[3])
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = int(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(edata))
		return (ctx, "") 
	
	if new > 20:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried setting maxsidelines to more than 20")
		new = "20"
	elif new < int(GameDict[gameid]["minsidelines"]):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried setting maxsidelines to less than minsidelines")
		new = GameDict[gameid]["minsidelines"]
		
	GameDict[gameid][subc] = str(new)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxsidelines")
	return (ctx, authorobj.mention + " The maxsidelines for game " + gameid + " was " + str(current) + " and is now " + str(new))

def GSpriorityamt(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSpriorityamt")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpriorityamt")
		return (ctx, authorobj.mention + " The priorityamt for game " + gameid + " is " + str(current))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking authority")
	authname = "changepriority"
	logger.debug(tb(tabs) + str(authname)+ ": " + SS["settings"]["authority"][authname])		
	if priv > int(SS["settings"]["authority"][authname]):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " User doesn't have permission to set " + adj + " status to fixed")
		return (ctx, authorobj.mention + " You don't have permission to change priority for a game")
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var with: " + uargs[3])
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = float(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an float: " + str(edata))
		return (ctx, authorobj.mention + " Please provide only a number") 
	
	if new > 20:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried setting priorityamt to more than 20")
		new = "20"
	elif new < 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tried setting priorityamt to less than 0")
		new = 0
		
	GameDict[gameid][subc] = str(new)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpriorityamt")
	return (ctx, authorobj.mention + " The priorityamt for game " + gameid + " was " + str(current) + " and is now " + str(new))
	
async def GSminlevel(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS minlevel")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]

	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminlevel")
		return (ctx, authorobj.mention + " The minlevel for game " + gameid + " is " + str(current))

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	# Check that it's an int
	if not IsInt(new):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wasn't given an int")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminlevel")
		return (ctx, authorobj.mention + " Provide only a number")
	
	# Check the length
	limit = StrToInt(GameDict[gameid]["maxlevel"])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Upper limit is currently " + GameDict[gameid]["maxlevel"])
	if limit != "" and StrToInt(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too high number given for limit " + GameDict[gameid]["maxlevel"])
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminlevel")
		return (ctx, authorobj.mention + " Set a number equal to or lower than " + GameDict[gameid]["maxlevel"])

	GameDict[gameid][subc] = str(new)

	result = authorobj.mention + " The minlevel for game " + gameid + " was " + str(current) + " and is now " + str(new)
	result += "\tIneligible players will be removed in the next audit cycle"
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The minlevel for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + str(new)
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSminlevel")
	return outputtup

async def GSmaxlevel(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS maxlevel")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 	= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command = uargs[0]
	gameid = uargs[1]
	subc = uargs[2]
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxlevel")
		return (ctx, authorobj.mention + " The maxlevel for game " + gameid + " is " + str(current))
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	# Check that it's an int
	if not IsInt(new):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wasn't given an int")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxlevel")
		return (ctx, authorobj.mention + " Provide only a number")
	
	# Check the length
	limit = StrToInt(GameDict[gameid]["minlevel"])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Lower limit is currently " + GameDict[gameid]["minlevel"])
	if limit != "" and StrToInt(new) < limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too high number given given for limit " + GameDict[gameid]["minlevel"])
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxlevel")
		return (ctx, authorobj.mention + " Set a number equal to or greater than " + GameDict[gameid]["minlevel"])

	GameDict[gameid][subc] = str(new)
	
	result = authorobj.mention + " The maxlevel for game " + gameid + " was " + str(current) + " and is now " + str(new)
	result += "\tIneligible players will be removed in the next audit cycle"
	outputtup = (ctx, result)

	# Updates	
	if GameDict[gameid]["completed"] == "0" and GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The maxlevel for " + guildobj.name + " game " + gameid + " was " + str(current) + " and is now " + str(new)
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSmaxlevel")
	return outputtup

def GSrosterlockbeforestart(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS GSrosterlockbeforestart")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSrosterlockbeforestart")
		return (ctx, authorobj.mention + " The rosterlockbeforestart for game " + gameid + " is set to " + str(current) + " minutes from game start (positive for before, negative for after)")
		
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = int(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(edata))
		return (ctx, "") 
	
	if new > 60*24*30: #minutes per day per month
		new = str(60*24*30)
	if new < 60*24*30*-1:
		new = str(60*24*30*-1)
		
	GameDict[gameid][subc] = str(new)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSrosterlockbeforestart")
	return (ctx, authorobj.mention + " The rosterlockbeforestart for game " + gameid + " was set to " + str(current) + " and is now set to " + str(new) + " minutes from game start (positive for before, negative for after)")

# ~~~ Toggles On/Off

def GSsidelineson(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS sidelineson")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	on 			= ["ON", "TRUE", "1", 1]
	off 		= ["OFF", "FALSE", "0", 0]
	
	setting = ["OFF", "ON"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning sidelineson")	
		message = authorobj.mention + " The sidelines are " + setting[int(current)] + " for game " + gameid
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + message)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsidelineson")
		return (ctx, message)

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	if new.upper() in on:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to true")
		GameDict[gameid][subc] = "1"
	elif new.upper() in off:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to false")
		GameDict[gameid][subc] = "0"
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Parameter given didn't match the right words for on/off")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsidelineson")
		return (ctx, authorobj.mention + " Choose ON or OFF")

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSsidelineson")
	return (ctx, authorobj.mention + " The sidelines for game " + gameid + " was " + setting[int(current)] + " and is now " + setting[int(GameDict[gameid][subc])])

def GSwhisperupdates(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS GSwhisperupdates")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSwhisperupdates")
		return (ctx, authorobj.mention + " The " + subc + " for game " + gameid + " is " + TOGGLEFT[StrToInt(current)])

	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new variable")
	
	# Make sure given value is valid
	new = uargs[3]
	if new.lower() not in TOGGLEON and new.lower() not in TOGGLEOFF:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wrong toggle answer given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSwhisperupdates")
		return (ctx, authorobj.mention + " Set to on or off")
	
	answer = "0"
	if new.lower() in TOGGLEON:
		answer = "1"
	GameDict[gameid][subc] = answer
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSwhisperupdates")
	return (ctx, authorobj.mention + " The " + subc + " for game " + gameid + " was " + TOGGLEFT[StrToInt(current)] + " and is now " + str(new))

async def GScompleted(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GScompleted")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	# Check for aliases and mispellings
	if subc.lower() in ["complete", ]:		
		logger.info('\t\t' + "Fixing alias: " + subc)
		uargs[2] = "completed"
		subc = uargs[2]
		
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
		
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GScompleted")
		return (ctx, authorobj.mention + " The completed status for game " + gameid + " is " + TOGGLEFT[StrToInt(current)])
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting variable")

	# Make sure given value is valid
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Validity check")
	new = uargs[3]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " New variable is " + new)
	if new.lower() not in TOGGLEON and new.lower() not in TOGGLEOFF:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wrong toggle answer given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GScompleted")
		return (ctx, authorobj.mention + " Set to true or false")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	answer = "0"
	if new.lower() in TOGGLEON:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting answer to 1")		
		answer = "1"
	GameDict[gameid][subc] = answer
	
	# Update the players' priorities
	if answer == "1":		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating Player Priorities")		
		roster = GameDict[gameid]["roster"]
		for pid, fixed in roster:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " checking player: " + str(pid))			
			pl = Serv["players"][pid]
			
			# remove from rostered
			if gameid in pl["r"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing game from pl[\"r\"]")
				pos = pl["r"].index(gameid)
				del pl["r"][pos]
			# check that it's not in sidelined
			if gameid in pl["s"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing game from pl[\"s\"]")
				pos = pl["s"].index(gameid)
				del pl["s"][pos]
			
			# add to played	
			if gameid not in pl["p"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding game to pl[\"p\"]")
				pl["p"].append(gameid)
		
		# Update the Game Master's record
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating the GM's record of gm'd games")
		gm = GameDict[gameid]["gm"]
		pl = Serv["players"][gm]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " GM is " + str(gm))
		
		# remove from game master rostered
		if gameid in pl["gr"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing game from pl[\"gr\"]")			
			pos = pl["gr"].index(gameid)
			del pl["gr"][pos]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pl[\"gr\"] is now " + str(pl["gr"]))
		
		# add to played	
		if gameid not in pl["gp"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding game to pl[\"pg\"]")			
			pl["gp"].append(gameid)

		# Release sidelines
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Releasing sidelined players")
		for pid, status in GameDict[gameid]["sideline"]:
			logger.debug(tb(tabs+1) + "checking player: " + str(pid))			
			pl = Serv["players"][pid]
			logger.debug(tb(tabs+1) + "pl: " + str(pl))
			
			# remove from sideline record
			RemovePlayerGameList(Serv, pid, gameid, "s", tabs=tabs+1)
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Clearing sideline list")
		GameDict[gameid]["sideline"].clear()	
				
	elif answer == "0" and current == "1": # UNcomplete the game, returning players to roster, etc
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " UNcompleting the game, returning players to roster etc")				
		
		# check authority level for toggling games Uncomplete
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority Check")
		Authorised = AuthorityCheck(SS, authorobj, "uncomplete", priv, command)
		if Authorised[0] == False:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Did not pass Authority Check")
			outputtup = (ctx, authorobj.mention + " You don't have permission to change a game from complete to incomplete")
			return outputtup
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")		
		
		roster = GameDict[gameid]["roster"]
		for pid, fixed in roster:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " checking player: " + str(pid))		
			pl = Serv["players"][pid]
			
			# remove from played	
			if gameid in pl["p"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing game from pl[\"p\"]")
				pos = pl["p"].index(gameid)
				del pl["p"][pos]
		
			# add to rostered
			if gameid not in pl["r"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding game to pl[\"r\"]")
				pl["r"].append(gameid)
	
		# Update the Game Master's record
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating the GM's record of gm'd games")
		gm = GameDict[gameid]["gm"]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " GM is " + str(gm))
		pl = Serv["players"][gm]
		
		# remove from played
		if gameid in pl["gp"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removing game from pl[\"gp\"]")
			pos = pl["gp"].index(gameid)
			del pl["gp"][pos]
		
		# add to rostered	
		if gameid not in pl["gr"]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " adding game from pl[\"gr\"]")
			pl["gr"].append(gameid)	

	else:
		outputtup = (ctx, authorobj.mention + " Game is already marked 'not complete'")
		return outputtup
	
	result = authorobj.mention + " The " + subc + " for game " + gameid + " was " + TOGGLEFT[int(current)] + " and is now " + TOGGLEFT[int(GameDict[gameid][subc])] + ".\nThe Priority Levels for rostered players have been updated"
	outputtup = (ctx, result)
	
	UpdateActiveGames(Serv, gameid, GameDict[gameid], tabs)
	
	# Updates	
	if GameDict[gameid]["published"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: Game " + gameid + " for " + guildobj.name + " was marked completed. \nIf you were rostered, your Priority Level has been adjusted to reflect this"
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
			
		# Published Embeds
		if GameDict[gameid][subc] != current: # making sure the user didn't just overwrite the setting with the same setting
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Unpublishing")
			await UpdateGameEmbeds(msg, gameid, "unpublish")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Republishing")
			await UpdateGameEmbeds(msg, gameid, "publish")
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GScompleted")
	return outputtup

async def GSpublish(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSpublish")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	
	# Check for aliases and misspellings
	if subc.lower() in ["publish", ]: # This is used for setting to true to reduce command excess
		logger.info('\t\t' + "Fixing alias: " + subc)
		uargs[2] = "published"
		subc = uargs[2]
		if args == 3: # setting to published true
			logger.info('\t\t' + "setting publish true")
			msg["uargs"].append("true")
			uargs 		= msg["uargs"]
			msg["numargs"] = len(uargs)
			args = msg["numargs"]
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No aliases found")
		
	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublish")
		return (ctx, authorobj.mention + " The published status for game " + gameid + " is " + TOGGLEFT[StrToInt(current)])
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Validity check")
	new = uargs[3]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " New variable is " + new)
	if new.lower() not in TOGGLEON and new.lower() not in TOGGLEOFF:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wrong toggle answer given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublish")
		return (ctx, authorobj.mention + " Set to true or false")
	
	outputtup = (ctx, "")

	if new.lower() in TOGGLEON:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publish turned on")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking that min and max level are set")
		levels = ["minlevel", "maxlevel"]
		for each in levels:
			if StrOrUnset(GameDict[gameid][each]) == "unset":
				logger.debug(tb(tabs) + each + "wasn't set")
				message = authorobj.mention + " " + each + " isn't set and is required. Use the following:\n"
				message += "!rb " + gameid + " " + each + " <number>"
				outputtup = (ctx, message)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublish")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " outputtup: " + str(outputtup))	
				return outputtup				
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Levels are set ok")		
		
		GameDict[gameid][subc] = "1"
		await UpdateGameEmbeds(msg, gameid, "publish")	
		message = authorobj.mention + " The published status for game "  + gameid + " was " + TOGGLEFT[int(current)].lower() + " and is now " + str(new)
		message += "\nPublished to game listing channel (if any)"
		outputtup = (ctx, message)
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating player records")
		if GameDict[gameid]["completed"] == "0":
			logger.debug(tb(tabs+1) + "Updating GM's rostered games")
			gmid = GameDict[gameid]["gm"]
			AddPlayerGameList(Serv, gmid, gameid, "gr")
			logger.debug(tb(tabs+1) + "Updating Player's rostered games")
			teams = [("roster", "r"), ("sideline", "s")]
			for (team, letter) in teams:
				for (pl, status) in GameDict[gameid][team]:
					AddPlayerGameList(Serv, pl, gameid, letter)
		elif GameDict[gameid]["completed"] == "1":
			logger.debug(tb(tabs+1) + "Updating GM's rostered games")
			gmid = GameDict[gameid]["gm"]
			AddPlayerGameList(Serv, gmid, gameid, "gp")
			logger.debug(tb(tabs+1) + "Updating Player's rostered games")
			team = ("roster", "p")
			for (pl, status) in GameDict[gameid][team[0]]:
				AddPlayerGameList(Serv, pl, gameid, team[1])					
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publish turned off")
		GameDict[gameid][subc] = "0"
		await UpdateGameEmbeds(msg, gameid, "unpublish")
		outputtup = (ctx, "The published status for game " + gameid + " was " + TOGGLEFT[int(current)].lower() + " and is now " + str(new) + ".\nRemoved from game listing channels (if any)")
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating player records")
		if GameDict[gameid]["completed"] == "0":
			logger.debug(tb(tabs+1) + "Updating GM's rostered games")
			gmid = GameDict[gameid]["gm"]
			RemovePlayerGameList(Serv, gmid, gameid, "gr")
			logger.debug(tb(tabs+1) + "Updating Player's rostered games")
			teams = [("roster", "r"), ("sideline", "s")]
			for (team, letter) in teams:
				logger.debug(tb(tabs+2) + "team: " + team)
				for (pl, status) in GameDict[gameid][team]:
					logger.debug(tb(tabs+3) + "pl: " + pl)
					RemovePlayerGameList(Serv, pl, gameid, letter)
		elif GameDict[gameid]["completed"] == "1":
			logger.debug(tb(tabs+1) + "Updating GM's rostered games")
			gmid = GameDict[gameid]["gm"]
			RemovePlayerGameList(Serv, gmid, gameid, "gp")
			logger.debug(tb(tabs+1) + "Updating Player's rostered games")
			teams = [("roster", "r"), ("sideline", "s")]
			for (team, letter) in teams:
				logger.debug(tb(tabs+2) + "team: " + team)
				for (pl, status) in GameDict[gameid][team]:
					logger.debug(tb(tabs+3) + "pl: " + pl)
					RemovePlayerGameList(Serv, pl, gameid, letter)	
	
	UpdateActiveGames(Serv, gameid, GameDict[gameid], tabs)
	
	# Updates	
	if GameDict[gameid]["completed"] == "0":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking update report")
		
		# DMs
		users = CollateUpdateMsgs(msg, gameid, "detail", tabs=tabs)
	
		if len(users):
			pairs = []
			for each in users:
				message = "NOTICE: The " + subc + " for " + guildobj.name + " was " + TOGGLEFT[int(current)].lower() + " and is now " + str(new)
				thispair = (each, message)
				pairs.append(thispair)
			pairs.append(outputtup)
			outputtup = (ctx, "List of outputups", pairs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No updates required")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSpublish")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " outputtup: " + str(outputtup))	
	return outputtup

def GenericSetting(msg, tabs=0):
	return (msg["ctx"], "There is no caller or modifier for this variable right now")

def GSrosterlockon(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSrosterlockon")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	on 			= ["ON", "TRUE", "1"]
	off 		= ["OFF", "FALSE", "0"]
	
	setting = ["OFF", "ON"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning rosterlockon")	
		message = authorobj.mention + " The rosterlockon state for game " + gameid + " is " + setting[int(current)]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + message)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSrosterlockon")
		return (ctx, message)

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	if new.upper() in on:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to true")
		GameDict[gameid][subc] = "1"
	elif new.upper() in off:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to false")
		GameDict[gameid][subc] = "0"
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Parameter given didn't match the right words for on/off")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSrosterlockon")
		return (ctx, authorobj.mention + " Choose ON or OFF")

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSrosterlockon")
	return (ctx, authorobj.mention + " The rosterlockon state for game " + gameid + " was " + setting[int(current)] + " and is now " + setting[int(GameDict[gameid][subc])])

def GSonlygmadd(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSonlygmadd")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	on 			= ["ON", "TRUE", "1"]
	off 		= ["OFF", "FALSE", "0"]
	
	setting = ["OFF", "ON"]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning onlygmadd")	
		message = authorobj.mention + " The onlygmadd state for game " + gameid + " is " + setting[int(current)]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + message)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSonlygmadd")
		return (ctx, message)

	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	if new.upper() in on:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to true")
		GameDict[gameid][subc] = "1"
	elif new.upper() in off:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Set to false")
		GameDict[gameid][subc] = "0"
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Parameter given didn't match the right words for on/off")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSonlygmadd")
		return (ctx, authorobj.mention + " Choose ON or OFF")

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSonlygmadd")
	return (ctx, authorobj.mention + " The onlygmadd state for game " + gameid + " was " + setting[int(current)] + " and is now " + setting[int(GameDict[gameid][subc])])

# ~~~ Reminders
def GSreminderson(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS GSreminderson")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " current is: " + str(current))
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSreminderson")
		return (ctx, authorobj.mention + " The " + subc + " for game " + gameid + " is " + TOGGLEOFFON[StrToInt(current)])

	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new variable")
	
	# Make sure given value is valid
	new = uargs[3]
	if new.lower() not in TOGGLEON and new.lower() not in TOGGLEOFF:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Wrong toggle answer given")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSreminderson")
		return (ctx, authorobj.mention + " Set to on or off")
	
	answer = "0"
	if new.lower() in TOGGLEON:
		answer = "1"
	GameDict[gameid][subc] = answer
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSreminderson")
	return (ctx, authorobj.mention + " The " + subc + " for game " + gameid + " was " + TOGGLEOFFON[StrToInt(current)] + " and is now " + TOGGLEOFFON[StrToInt(answer)])

def GSremindwhen(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GS GSremindwhen")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSremindwhen")
		return (ctx, authorobj.mention + " The remindwhen for game " + gameid + " is set to " + str(current) + " minutes before game start")
		
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = uargs[3]
	try:
		new = int(new) # convert to int
	except Exception as e:
		edata = PrintException()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(edata))
		return (ctx, "") 
	
	if new > 60*24: #minutes per day
		new = str(60*24)
	if new < 0:
		new = 0
		
	GameDict[gameid][subc] = str(new)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSremindwhen")
	return (ctx, authorobj.mention + " The remindwhen for game " + gameid + " was set to " + str(current) + " and is now set to " + str(new) + " minutes before game start")

def GSremindermsg(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GSremindermsg")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]

	GameDict = Serv["games"]
	current = GameDict[gameid][subc]
	
	# Get
	if args == 3:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSremindermsg")
		return (ctx, authorobj.mention + " The reminder message for " + guildobj.name + " game " + gameid + " is\n" + str(current))
	
	# Set
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting new var")
	
	# Make sure given value is valid
	new = " ".join(uargs[3:])
	# Check the length
	limit = 280
	if len(new) > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many characters given for limit " + str(limit))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSremindermsg")
		return (ctx, authorobj.mention + " Limit your reminder message to under " + str(limit) + " characters")
	
	GameDict[gameid][subc] = new
	
	result = authorobj.mention + " The reminder message for " + guildobj.name + " game " + gameid + " was \n" + str(current) + "\nand is now\n" + str(new)
	outputtup = (ctx, result)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSremindermsg")
	return outputtup

def Greminders(msg, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of Greminders")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"]
	current 	= GameDict[gameid][subc]
	
	# Get
	result = authorobj.mention + " Number of reminders sent: " + str(len(current))
	for pl, mid in current.items():
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " This pl: " + str(pl))
		member = guildobj.get_member(int(pl))
		result += "\n\t" + member.mention + " (mid: " + str(mid) + ")"
	
	outputtup = (ctx, result)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Greminders")
	return outputtup

def SendMessage(msg, tabs=0):
	""" Sends a given message to all on the roster, sidelines, or all/both """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of SendMessage")
	tabs += 1
	
	# Easy access variables
	guildobj 	= msg["guild"]			# the discord guild object
	Serv 		= msg["serverdata"]		# my data dictionary for this guild
	SS 			= msg["ss"]				# the "server settings" dictionary for this guild
	AC 			= msg["ac"]				# the generic "all commands" dictionary for the bot
	authorobj	= msg["author"]			# the discord member object
	uargs 		= msg["uargs"]			# the words given by the author
	args 		= msg["numargs"]		# int for the number of words given
	priv		= msg["authority"]		# int for the author's authority level
	ctx 		= msg["ctx"]			# the context bot thing
	command 	= uargs[0]
	gameid 		= uargs[1]
	subc 		= uargs[2]
	GameDict 	= Serv["games"][gameid]
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting the message to send")
	message = " "
	if ":" in " ".join(uargs): # separator of args from message
		joined = " ".join(uargs)
		cut = joined.split(":", 1)
		message = cut[1]
		uargs = cut[0].split()
		args = len(uargs)
		
		if len(message) == 0:
			output = (ctx, authorobj.mention + " Please provide a message to send")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of SendMessage")
			return output			
	elif args == 3:
		output = (ctx, authorobj.mention + " Please provide a message to send")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of SendMessage")
		return output
	else:
		message = " ".join(uargs[3:])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " message is: " + message)
	

	fixed = True
	unfixed = True
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Gathering who to send to")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking for all/roster/sideline")
	lists = []
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Gathering who to send to")
	if subc in ["msgroster", "msgrosters", "messageroster", "messagerosters"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Said roster only")
		lists.append("roster")
	elif subc in ["msgsideline", "msgsidelines", "messagesideline", "messagesidelines"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Said roster only")
		lists.append("sideline")
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Default send to all")
		lists.append("roster")
		lists.append("sideline")		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " lists is: " + str(lists))

	recip = []
	names = []
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting players")
	unfound = False
	for sublist in lists:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting from " + sublist + ": " + str(GameDict[sublist]))
		for pid, status in GameDict[sublist]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pid: " + str(pid) + ", status: " + str(status))		
			player = None
			tries = 0
			while player == None and tries < 3:
				if tries != 0:
					time.sleep(0.5)
				player = GetMember(ctx, pid, tabs=tabs+1)
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player: " + str(player))
				tries += 1
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Tries: " + str(tries))
			if player == None:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't find player with pid: " + str(pid))
				unfound = True
			else:
				recip.append(player)
				names.append(player.mention)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " recip: " + str(recip))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " names: " + str(names))
	
	messagelist = []
	thismsg = authorobj.mention + "Sending message to: " + " ".join(names) + " for game " + gameid + "\n" + message
	if unfound:
		thismsg += "/n(One or more players couldn't be found by Discord. Maybe they left?)"
	reply = (ctx, thismsg)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " reply: " + str(reply))
	messagelist.append(reply)
	
	for each in recip:
		quote = (each, "You have been sent the following message from " + authorobj.mention + " for game " + gameid + ":\n" + message)
		messagelist.append(quote)
	outputtups = (ctx, "List of outputups", messagelist)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " messagelist: " + str(messagelist))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of SendMessage")
	return outputtups