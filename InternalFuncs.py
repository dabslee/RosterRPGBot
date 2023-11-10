from config import *
import logging
import inspect
import time
import inspect
import pytz
import copy
import asyncio
import Dserver
from datetime import datetime, timedelta
from Commands import *
from GameData import *
from discord import Embed, utils, DiscordException, NotFound, HTTPException, Forbidden

	# Easy access variables
	# guildobj 		= msg["guild"]
	# serverdata 	= msg["serverdata"]
	# ss 			= msg["ss"]
	# ac 			= msg["ac"]
	# authorobj		= msg["author"]
	# ctx 			= msg["ctx"]
	# uargs 		= msg["uargs"]
	
# ~~~~~~~~~~~~~~~~~~~~~~~~ Internal Worker Functions
def GetAuthorAuthority(guild, user, roles, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Beginning of GetAuthorAuthority")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Data received: " + str([guild, user, roles]))
	
	# get the user's roles
	uroles = user.roles
	output = 4
	urids = [str(r.id) for r in user.roles]
	
	if user.id == guild.owner_id:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Author is guild owner")
		output = 1
	elif user.id == AUTHORID:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Author is bot creator")
		output = 1
	elif len(roles["4"]) > 0 and len([rid for rid in roles["4"] if rid in urids]) > 0:	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Level 4 (exclusion) role")
		output = 4
	elif len(roles["1"]) != 0 and len([rid for rid in roles["1"] if rid in urids]) > 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Level 1 role")
		output = 1	
	elif len(roles["2"]) == 0 or len([rid for rid in roles["2"] if rid in urids]) > 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Level 2 role")
		output = 2
	elif len(roles["3"]) == 0 or len([rid for rid in roles["3"] if rid in urids]) > 0:	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Level 3 role")
		output = 3
	
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetAuthorAuthority")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Output is: " + str(output))
	return output	
		
def GetUser(ctx, pid, tabs=0): # Not used
	# """ Takes a single user ID and returns the Discord member object """
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetUser: pid " + str(pid))
	# tabs += 1
	# 
	# user = ctx.bot.get_user(StrToInt(pid))
	# 
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning member " + str(user))		
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetUser")
	# return user
	pass

def GetMember(ctx, pid, tabs=0):
	""" Takes a single user ID and returns the Discord member object """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetMember: pid " + str(pid))
	tabs += 1
	
	member = ctx.guild.get_member(StrToInt(pid, tabs=tabs+1))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Returning member " + str(member))		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetMember")
	return member

def ConvertRoleIDToNameList(ctx, RoleIDs, tabs=0):
	""" Converts a list of role IDs to a list of tuples
	of ID, Name """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ConvertRoleIDsToName: " + str(RoleIDs))
	tabs += 1
	converted = []
	for each in RoleIDs:
		converted.append((each, ctx.message.guild.get_name(each)))
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converted list: " + str(converted))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of BotInfoBox")
	return converted

def ConvertRoleIDToNameSingle(ctx, RoleID, tabs=0):
	""" Takes a single role ID and converts to it's name """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ConvertRoleIDToNameSingle: " + str(RoleID))
	tabs += 1
	
	name = None
	groles = ctx.message.guild.roles
	for role in groles:
		if role.id == RoleID:
			name = role.name
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Matching role " + str(name) + " matches ID " + str(RoleID))		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of BotInfoBox")
	return name

def ConvertRoleIDsToRoles(ctx, guild, roleIDs, tabs=0):
	""" Takes a list of Role IDs and returns a list of Discord Role Objects """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ConvertRoleIDsToRoles: guild " + str(guild.name) + ", roleIDs " + str(roleIDs) )
	tabs += 1
	
	result = []
	
	# Get the guild's roles and check the members
	for each in roleIDs:
		role = guild.get_role(StrToInt(each))
		if role not in [False, None]:
			result.append(role)				
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roles found for list of roles " + str(result))		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ConvertRoleIDsToRoles")
	return result			
	
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Matching role " + str(name) + " matches ID " + str(RoleID))		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ConvertRoleIDsToRoles")
	return name	

def CheckUserHasRole(ctx, guildid, pid, roleIDs, tabs=0): # Not used?
	# """ Takes a single user ID, gets their roles and checks them in a list of roleIDs """
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CheckUserHasRole: guildid " + str(guildid) + ", pid " + str(pid) + ", roleIDs " + str(roleIDs) )
	# tabs += 1
	# 
	# result = False
	# 
	# # Get the user
	# user = GetUser(ctx, pid)
	# if user in [False, None]:
	# 	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching role found for pid " + str(pid))		
	# 	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckUserHasRole")
	# 	return False
	# 
	# # Get the guild
	# guild = ctx.bot.get_guild(StrToInt(guildid))
	# if guild in [False, None]:
	# 	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching guild found for guildid " + str(guildid))		
	# 	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckUserHasRole")
	# 	return False		
	# 
	# # Get the guild's roles and check the members
	# found = False
	# for each in roleIDs:
	# 	role = guild.get_role(StrToInt(each))
	# 	if role not in [False, None]:
	# 		# Check the members
	# 		if user in role.members:
	# 			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Found a matching role")		
	# 			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckUserHasRole")
	# 			return True					
	# 	
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No matching roles found for list of roles " + str(roleIDs))		
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckUserHasRole")
	# return False			
	# 
	# 
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Matching role " + str(name) + " matches ID " + str(RoleID))		
	# logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckUserHasRole")
	# return name
	pass
	
def CreateGameID(timestring, gmdisplay, tabs=0):
	""" Creates a (hopefully) unique game id """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CreateGameID. " + " ".join([timestring, gmdisplay]))
	tabs += 1
	
	timestring = timestring.replace(" ", "")
	gmid = ""
	if len(gmdisplay) >= 3: # in case a gm somehow has fewer characters, or for creating these time strings without a gmdisplay name
	
		gmid = timestring[2:-3] + gmdisplay[:3].lower()
	else:
		gmid = timestring[2:-3] + gmdisplay[:].lower()
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game ID is " + gmid)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CreateGameID")
	return gmid

def ConvertTimezone(FromZone, timestring, ToZone, fromformat=TFORMAT, toformat=TFORMAT, tabs=0):
	""" Takes a string in the format "%Y %m %d %H:%M" and turns it from one
	timezone to another """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ConvertTimezone from " + str(FromZone) + " " + timestring + " to " + str(ToZone))
	tabs += 1
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking that FROM timezone is a valid format")
	try:
		ftz = pytz.timezone(FromZone)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ftz: " + str(ftz))
	except (Exception, DiscordException) as e:
		logger.error(tb(tabs) + "There was an error converting timezone " + str(FromZone))
		logger.error(tb(tabs) + str(e))
		return e # this must be an error object and NOT a string

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking that TO timezone is a valid format")	
	if type(ToZone) != type(""):
		print("ToZone, " + str(ToZone) + " is not a string for some reason??")
	try:
		ttz = pytz.timezone(ToZone)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ttz: " + str(ttz))
	except (Exception, DiscordException) as e:
		edata = PrintException()
		logger.error(tb(tabs) + "There was an error converting timezone " + str(ToZone))
		logger.error(tb(tabs) + str(edata))
		return e # this must be an error object and NOT a string
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating datetime objects from the given time string")		
	try:
		# Getting the FromTime as a time object
		dt_str = datetime.strptime(timestring, fromformat)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dt_str: " + str(dt_str))
		dt_obj_ftz = ftz.localize(dt_str) #localising accounts for daylight savings		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dt_obj_ftz: " + str(dt_obj_ftz))
	except (Exception, DiscordException) as e:
		edata = PrintException()
		logger.error('\t' + "There was an error converting timestring " + timestring)
		logger.error('\t' + str(edata))
		return e # this must not return the string edata. If it does, the game creator won't know there was an arror
				 
	totime = dt_obj_ftz.astimezone(ttz)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Result is " + totime.strftime(toformat))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StringToUTCTime")
	return totime.strftime(toformat)

def GetGameDateTime(Serv, gid, tz="UTC", tformat=TFORMAT, tabs=0):
	""" Returns the timezone, date and time of the given game as a string """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetGameDateTime. gid: " + str(gid) + " tz: " + str(tz))
	tabs += 1
	
	Game = Serv["games"][gid]
	
	rtz = None # Just gotta test that the given tz is usable before passing it
	try:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Trying to convert timezone " + str(tz))
		rtz = pytz.timezone(tz)
	except (Exception, DiscordException) as e:
		edata = PrintException()
		logger.error('\t' + "There was an error converting timezone " + str(tz))
		logger.error('\t' + str(edata))
		return "That timezone makes no sense!"
		

	timestr = tz + " " + ConvertTimezone(Game["timezone"], Game["datetime"], tz, TFORMAT, TDFORMAT, tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Result is " + timestr)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetGameDateTime")
	return timestr

def GameFunctions(ctx, Serv, SS, AC, uargs, priv, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GameFunctions. uargs: " + str(uargs))
	tabs += 1
	command = uargs[0]
	args = len(uargs)
	gameid = uargs[1].lower()
	
	# Check if a game with the given id exists
	Games = Serv["games"]
	if gameid not in Games:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No game for " + gameid + " found")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameFunctions")
		return "No such game found"		
		
	if args == 2:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only game info requested for game " + gameid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameFunctions")
		return PrintGameInfo(ctx, Serv, SS, AC, uargs, priv)
	
	# Clean remainder text of malicious characters
	if args > 3:
		for each in uargs[3:]:
			for char in MALICIOUS:
				if char in each:
					logger.warning(('\t' * tabs) + "Malicious character " + char + " detected")
					print("Malicious character " + char + " detected: " + " ".join(uargs))
					return "Do not use the " + char + " character"
			
		
	# Handle Subcommand
	subc = uargs[2]
	if subc not in AC[command]["getset"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Non-existant Game Subcommand given: " + subc)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameFunctions")
		return ""

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GameFunctions")
	return AC[command]["getset"][subc](ctx, Serv, SS, AC, uargs, priv)

def GetCharLevel(nick, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetCharLevel for " + str(nick))
	tabs += 1
	dig1 = ""
	dig2 = ""
	
	if IsInt(str(nick)[-1], tabs):
		dig1 = str(nick)[-1]
	else:
		return "Display name not formatted to show level as last two characters"
	
	if len(str(nick)) > 1 and IsInt(str(nick)[-2], tabs):
		dig2 = str(nick)[-2]
	else:
		return "Display name not formatted to show level as last two characters"
	
	level = StrToInt(dig2 + dig1, tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Display name converted to level: " + str(level))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetCharLevel")
	return level
	
def CheckConsecutiveRosters(Serv, pid, listedgame, tabs=0):
	"""Checks whether too many consecutive games have been played.
	If so, returns True. If not, returns False """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CheckConsecutiveRosters for " + str(pid))
	tabs += 1
	player = Serv["players"][pid]
	# Get only played games, not rostered, sidelined or gm'd
	played = player["p"][:] + player["l"][:]
	played.sort()		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " player's played games: " + str(played))
	
	maxcon = int(Serv["settings"]["playermaxconsecutive"])
	if maxcon == -1 or len(played) <= maxcon:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Few enough games played to pass")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckConsecutiveRosters")
		return False
	
	games = sorted(Serv["games"].keys())
	pos = games.index(listedgame)
	if pos > maxcon:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too few games in the server list to matter")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckConsecutiveRosters")
		return False
	prevset = games[pos-maxcon:pos]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " The game/s set to check: " + str(prevset))
	
	# Check if the consecutive games in the Server Games list is in the player's played games.
	if (set(prevset).issubset(set(played))):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Too many consecutive games matched, prevset " + str(prevset) + ", games played " + str(played))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckConsecutiveRosters")
		return True
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckConsecutiveRosters")
	return False

def CalcPlayerPriority(Serv, pid, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CalcPlayerPriority for player " + pid)
	tabs += 1
	player = Serv["players"][pid]
	# Get only played games, not future rostered, sidelines, or last game from previous week
	played = player["p"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " player's played games: " + str(played))
	sumprio = 0
	for each in played:
		current = float(Serv["games"][each]["priorityamt"])
		logger.debug(tb(tabs+1) + each + " priorityamt: " + str(current))
		sumprio += current
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " sumprio: " + str(sumprio))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CalcPlayerPriority")
	return sumprio

def RemovePlayerGameList(Serv, pid, gid, listletter, tabs=0):
	""" Removes the given gid from the player's game list. Doesn't make any other changes """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of RemovePlayerGameList for pid " + str(pid) + " and gid " + str(gid) + " with listletter " + str(listletter))
	tabs += 1
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's game list was: " + str(Serv["players"][pid]))
	plist = Serv["players"][pid][listletter]
	while gid in Serv["players"][pid][listletter]:
		logger.debug(tb(tabs+1) + "Found it. Deleting")
		Serv["players"][pid][listletter].remove(gid)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's game list is now: " + str(Serv["players"][pid]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of RemovePlayerGameList")

def AddPlayerGameList(Serv, pid, gid, listletter, tabs=0):
	""" Adds the given gid from the player's game list. Doesn't make any other changes """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of AddPlayerGameList for pid " + str(pid) + " and gid " + str(gid) + " with listletter " + str(listletter))
	tabs += 1
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's game list was: " + str(Serv["players"][pid]))
	plist = Serv["players"][pid][listletter]
	if gid not in Serv["players"][pid][listletter]:
		Serv["players"][pid][listletter].append(gid)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player's game list is now: " + str(Serv["players"][pid]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of AddPlayerGameList")

def RemoveFromTeam(Serv, gameid, pid, team="roster", removefixed=False, tabs=0):
	""" Flat deletes a player from the roster without adding to sidelines or promoting a replacement
	Returns True for deletion, False for no found, and -1 for no authority to move """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removefixed: " + str(removefixed))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of RemoveFromTeam for gameid " + gameid + " and player id " + pid + ", removefixed: " + TOGGLEFT[removefixed])
	tabs += 1
	GameDict = Serv["games"][gameid]
	
	result = False
	cleanrecord = True
	logger.debug(tb(tabs) + team + " len: " + str(len(GameDict[team])))
	logger.debug(tb(tabs) + team + ": " + str(GameDict[team]))
	tcopy = [(num, each[0], each[1]) for num, each in enumerate(GameDict[team][:])]
	for num, memberid, fixed in tcopy[::-1]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking " + str(num) + ". pid: " + str(memberid) + ". status: " + str(fixed))
		if pid == memberid:			
			logger.debug(tb(tabs+1) + "Matched. Player IS in the " + team)
			if fixed == "fixed" and removefixed == False:
				logger.debug(tb(tabs+1) + "Player is fixed and removedfixed is false")
				result = -1
				cleanrecord = False
			else:
				logger.debug(tb(tabs+1) + "Removing")
				del Serv["games"][gameid][team][num]
				result = True
				# Removing the game from the Player's games list
				logger.debug(tb(tabs+1) + "Will be updating player's game list")
				logger.debug(tb(tabs+1) + team + " now: " + str(GameDict[team]))
		else:
			logger.debug(tb(tabs+1) + "Not a match")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished removing all records of the player in this team")
	logger.debug(tb(tabs) + team + " now: " + str(GameDict[team]))
	if cleanrecord:
		group = 'r'
		if team == "sideline":
			group = 's'
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Cleaning player's record")
		RemovePlayerGameList(Serv, pid, gameid, group, tabs=tabs)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No need to clean player's record")
		
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of RemoveFromTeam")
	return result

def ConvertPIDsToNames(bot, Serv, ids, nameformat="display_name", tabs=0):
	"""Takes a list of discord User IDs and returns them as a list of their names
	Name format can be "display_name" or "mention" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ConvertPIDsToNames with nameformat " + str(nameformat) + " for names: " + str(ids))
	tabs += 1

	names = []
	sid = Serv["GuildID"]
	guild = utils.get(bot.guilds, id=sid)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild ID is: " + str(guild) + " " + str(type(guild)))
	
	for num, pid in enumerate(ids):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " This pid: " + str(pid))
		member = guild.get_member(int(pid)) #utils.get(guild.members, id=pid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Member is " + str(member))
		if member == None:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Member left the guild")
			names.append(str(pid) + " (left)")
		elif nameformat == "display_name":
			names.append(member.display_name)
		else:
			names.append(member.mention)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Result is:" + str(names))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ConvertPIDsToNames")
	return names

def CheckRosterLocked(gamedict, tabs=0):
	""" Checks if the roster has locking turned on if now is within that lock period """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CheckRosterLocked for guild: " + str(gamedict["id"]))
	tabs += 1
		
	locked 	= gamedict["rosterlockon"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " locked: " + str(locked))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if roster is locked")
	if locked == "0":
		logger.debug(tb(tabs+1) + "Roster is not locked. End of CheckRosterLocked")
		return False
	else:
		logger.debug(tb(tabs+1) + "Roster has locked turned on, checking if in locked periodf")
		
	when = gamedict["rosterlockbeforestart"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " when: " + str(when))	
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting game time")
	gtz = pytz.timezone(gamedict["timezone"])
	gametime = gamedict["datetime"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gametime: " + gtz.zone + " " + gametime)
	gt_dt = gtz.localize(datetime.strptime(gametime, TFORMAT))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gt_dt: " + str(gt_dt))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting minutes to subtract")
	subtract_td = timedelta(minutes=int(when))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting roster locked time")
	rtime_dt = gt_dt - subtract_td
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " rtime_dt: " + str(rtime_dt))
	utc = pytz.timezone("UTC")
	now = datetime.now(utc) # a datetime object of now, using the game's timezone
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now: " + str(now))
	then = rtime_dt.astimezone(utc)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then: " + str(then))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if roster lock time has passed")
	if now < then:
		logger.debug(tb(tabs+1) + "Not time yet. Returning false")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckRosterLocked")
		return False
	else:
		logger.debug(tb(tabs+1) + "Locked time has passed. Returning True")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckRosterLocked")
		return True

def GetGameInfoEmbed(bot, Serv, gameid, timezone, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetGameInfoEmbed for gameid " + str(gameid) + " in timezone " + str(timezone))
	tabs += 1
	Game = Serv["games"][gameid]
	#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game data: " + str(Game)) 
	sid = Serv["GuildID"]
	guild = utils.get(bot.guilds, id=sid)
	#logger.debug(tb(tabs)+ "Serv:")
	#deeplogdict(Serv, "debug", tabs+1)
	
	# Get the Date Time, converted if necessary
	gtz = Game["timezone"]
	gdt = Game["datetime"]
	dtstr = gtz + " " + gdt
	if timezone != None and timezone != gtz:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting to from " + gtz + " to " + timezone)
		dtstr = GetGameDateTime(Serv, gameid, timezone, tformat=TDFORMAT, tabs=tabs)
	else:
		dtstr = GetGameDateTime(Serv, gameid, gtz, tformat=TDFORMAT, tabs=tabs)
	
	if dtstr == " ":
		dtstr = ""
	
	GM = guild.get_member(StrToInt(Game["gm"], tabs=tabs))
	if GM != None:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game Master found: " + str(GM.name))
		GM = GM.display_name
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No GM found. Probably left the guild")
		GM = Game["gm"] + "(left)"
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding fields to embed object")
	infobox = Embed()
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting name " + Game["name"])
	infobox.title = StrOrUnset(Game["name"])
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting image " + str(Game["image"]))
	if Game["image"] not in ["", None, "None", "none", "NONE"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting an image")
		infobox.set_image(url=Game["image"])
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting id " + Game["id"])
	infobox.add_field(inline=True,  name="id", 			value=StrOrUnset(Game["id"]))	
	#if Serv["settings"]["levelcapson"] == "1":
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting levelcaps " + Game["minlevel"] + " " + Game["maxlevel"])
	infobox.add_field(inline=True,  name="Levels", 		value=StrOrUnset(Game["minlevel"])+"-"+StrOrUnset(Game["maxlevel"]))
	#else:
		#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " NOT Setting levelcaps ")
	if Serv["settings"]["prioritieson"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting priorityamt " + Game["priorityamt"])
		infobox.add_field(inline=True,  name="+Priority", 	value=str(Game["priorityamt"]))
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " NOT Setting priorityamt ")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting time " + StrOrUnset(dtstr))
	infobox.add_field(inline=True,  name="Time", 		value=StrOrUnset(dtstr))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting duration " + Game["duration"])
	infobox.add_field(inline=True,  name="Duration", 	value=StrOrUnset(Game["duration"]))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting description " + Game["description"])
	infobox.add_field(inline=False, name="Description",	value=StrOrUnset(Game["description"]))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting GM " + GM)
	infobox.add_field(inline=False, name="GM", 			value="```" + GM + "```")
	
	# Get Roster list
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting roster pids to names")	
	names = ConvertPIDsToNames(bot, Serv, [each[0] for each in Game["roster"]], tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Names are: " + str(names))
	ps = "```\n"
	for num, name in enumerate(names):
		logger.debug(tb(tabs+1) + "name: " + name)
		#ps = ""
		if Serv["settings"]["prioritieson"] == "1":
			P = CalcPlayerPriority(Serv, Game["roster"][num][0], tabs=tabs)
			if P % 1 == 0: # Remove decimal place if not needed
				P = int(P)
			ps += str(num+1) + " " + name + " P" + str(P)
		else:
			ps += str(num+1) + " " + name
		logger.debug(tb(tabs+1) + "status: " + str(Game["roster"][num][1]))
		if Game["roster"][num][1] == "fixed":
			ps += " (f)"
		ps += "\n"
	
	# pad the rest of the list out with blank lines
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Padding the rest of the list")
	maxp = Game["maxplayers"]
	lenrost = len(Game["roster"])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " maxplayers: " + maxp)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " calculating and printing rows for roster, len: " + str(lenrost))	
	if IsInt(maxp, tabs=tabs) and lenrost < StrToInt(maxp, tabs=tabs):
		diff = StrToInt(maxp, tabs=tabs) - lenrost
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " diff: " + str(diff))
		for each in range(diff):
			logger.debug(tb(tabs+1) + "each: " + str(each))
			ps += str(each+lenrost+1) + "\n"
	ps += "```\n"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting rosterlocked")
	fname = "Roster"
	if Game["onlygmadd"] == "1":
		fname += " (only GM add)"
	elif Game["rosterlockon"] == "1":
		crl = CheckRosterLocked(Game, tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " crl: " + str(crl))
		if crl:
			fname += " LOCKED"
		else:
			fname += " (lock: " + Game["rosterlockbeforestart"] + " mins)"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " fname: " + str(fname))	
	infobox.add_field(inline=True, name=fname, value=ps)	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roster is: \n" + str(ps))
	
	# Get Sideline list
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting sidelines")
	names = ConvertPIDsToNames(bot, Serv, [each[0] for each in Game["sideline"]], tabs=tabs)
	strike = "~~"
	if Game["sidelineson"] == "1":
		strike = ""
	ps = strike + "```\n"
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " calculating and printing rows for sidelines")	
	for num, name in enumerate(names):
		#ps = ""
		if Serv["settings"]["prioritieson"] == "1":
			P = CalcPlayerPriority(Serv, Game["sideline"][num][0], tabs=tabs)
			if P % 1 == 0: # Remove decimal place if not needed
				P = int(P)
			ps += strike + str(num+1) + " " + name + "  P" + str(P)
		else:
			ps += strike + str(num+1) + " " + name
			
		if Game["sideline"][num][1] == "fixed":
			ps += " (f)"
		ps += "\n"
	if ps == (strike + "```\n"): # No-one listed in sidelines
		ps = "-"
	else:
		ps += "```" + strike + "\n"
	infobox.add_field(inline=True, name="Sidelines", value=ps)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sidelines is: " + str(ps))
	
	compl = TOGGLENY[StrToInt(Game["completed"], tabs=tabs)]
	infobox.add_field(inline=False, name="Completed", value=compl)	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Completed is: " + compl)
	
	tc = guild.get_channel(StrToInt(Game["textchannel"], tabs=tabs))
	if tc == None:
		tc = "unset"
	else:
		tc = tc.mention
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " text channel is: " + tc)	
	infobox.add_field(inline=True, name="Text", value=tc)
		
	vc = guild.get_channel(StrToInt(Game["voicechannel"], tabs=tabs))
	if vc == None:
		vc = "unset"
	else:
		vc = vc.mention
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " voice channel is: " + vc)
	infobox.add_field(inline=True, name="Voice", value=vc)
	
	#Game["image"]
	#Game["linkchronus"]
	#Game["link"]
	link = StrOrUnset(Game["link"], tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " link is: " + link)
	infobox.add_field(inline=True, name="Link", value=link)
	
	pub = ["unpublished", "published"]
	publi = pub[StrToInt(Game["published"], tabs=tabs)]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " publish is: " + publi)
	infobox.set_footer(text=publi)
	
	# Randomly select a colour for now
	reds = {"red": 0xe74c3c, "dark_red": 0x992d22, "magenta": 0xe91e63, "dark_magenta": 0xad1457}
	if publi == "unpublished":
		infobox.color = random.choice(list(reds.values()))
	else:
		infobox.color = random.choice(list(COLOURS.values()))
		while infobox.color in reds.values():
			infobox.color = random.choice(list(COLOURS.values()))

	#print(str(infobox.fields))
	logger.debug(tb(tabs) + str(infobox.fields))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GetGameInfoEmbed")
	return infobox

# Copyright Ferry Boender, released under the MIT license.
def deepupdate(target, src):
    """Deep update target dict with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it.

    Examples:
    >>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> print t
    {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi', 'gaming']}
    copied from https://www.electricmonk.nl/log/2017/05/07/merging-two-python-dictionaries-by-deep-updating/
    on 21/08/2020
    """
    for k, v in src.items():
        if type(v) == list:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        elif type(v) == set:
            if not k in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)

async def DirectMessagePlayer(guildobj, pid, messagestr, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of DirectMessagePlayer")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pid: " + str(pid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " message: " + messagestr)
	member = utils.get(guildobj.members, id=int(pid))
	await member.send(messagestr)	
	
async def PromoteFromSidelines(bot, Serv, gid, movefixed=False, tabs=0):
	""" Promotes a player from the Sidelines """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of PromoteFromSidelines")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gid: " + str(gid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " movefixed: " + str(movefixed))
	GameDict	= Serv["games"][gid]
	roster 		= GameDict["roster"]
	sideline	= GameDict["sideline"]
	maxp 		= GameDict["maxplayers"]
	maxsp		= GameDict["maxsidelines"]
	guildobj	= bot.get_guild(int(Serv["GuildID"]))
	logger.debug(tb(tabs)+ "GameDict:")
	#deeplogdict(GameDict, "debug", tabs+1)
	# logger.debug(tb(tabs) + str(GameDict)) # Already printed in AuditRoster
	
	# Step 1: Check that there are sidelines
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1: Check that there are sidelines: " + str(sideline))
	if len(sideline) == 0:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No sidelined players")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PromoteFromSidelines")
		return False

	# Step 1.1: Check that "onlygmadd" isn't on
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1.1: Check that onlygmadd isn't on: " + str(GameDict["onlygmadd"]))
	if GameDict["onlygmadd"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Only GMs can promote players")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PromoteFromSidelines")
		return False
	
	# Step 2: Get roster sorted by priority
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2: Get roster sorted by priority")
	insertpos = -1
	sortside = []
	if Serv["settings"]["prioritieson"] == "0":
		logger.debug(tb(tabs+1) + "Priorities are off")
		if len(roster) < int(maxp):
			logger.debug(tb(tabs+1) + "There's a spot at the end of the roster")
			insertpos = len(roster) + 1
			sortside = sideline[:]
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No free spots")
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PromoteFromSidelines")
			return False
	else:				
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Priorities are on")
		
		def PSortRoster(roster, movefixed=False, tabs=0):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of PSortRoster")
			logger.debug(tb(tabs+1) + "Roster: " + str(roster))
			croster = [(pos, pl, CalcPlayerPriority(Serv, pl, tabs+2), fixed) for pos, (pl, fixed) in enumerate(roster)] # filtered copy of roster
			logger.debug(tb(tabs+1) + "croster: " + str(croster))
			croster = sorted(croster, key=lambda element: (element[2], element[0]))
			logger.debug(tb(tabs+1) + "sorted croster: " + str(croster))
			logger.debug(tb(tabs+1) + "End of PSortRoster")
			return croster
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding blank lines to croster")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " maxp: " + str(maxp) + " | len of roster:" + str(len(roster)))
		croster = GameDict["roster"][:] # copy of the roster
		croster = PSortRoster(croster, movefixed, tabs+1)
		diff = int(maxp) - len(roster) # must use roster rather than croster
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if roster is locked")
		if diff <= 0 and CheckRosterLocked(GameDict, tabs):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roster is full and locked")
			filled = False
			return filled
	
			
		logger.debug(tb(tabs+1) + "Need to add " + str(diff) + " blank lines")
		ele = len(roster) #next blank spot	
		while ele < int(maxp):
			logger.debug(tb(tabs+2) + "Adding blank ele " + str(ele))
			croster.append((ele, None, 10000, "unfixed"))
			ele += 1
		
		# Step 3: Get the highest priority sidelined player
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 3: Get the highest priority sidelined player")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " sideline is: " + str(sideline))
		prios = [(pos, pl, CalcPlayerPriority(Serv, pl, tabs+1), fixed) for pos, (pl, fixed) in enumerate(sideline)]
		sortside = sorted(prios, key=lambda element: (element[2], element[0]))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sortside: " + str(sortside))
		
		
		# Step 4: Go through each in priority order and find the next eligible
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4: Go through each in priority order and find the next eligible")
		demote = False	
		while(insertpos == -1 and len(sortside)):	
			thispl 	= sortside[0]
			sid		= thispl[1]
			pnum 	= thispl[2]
			sfixed  = thispl[3]
			logger.debug(tb(tabs+1) + "Checking " + str(sortside[0]))
			tabs+=2
			# Step 4.1: Check that they're not already in the list
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.1: Check that they're not already in the list")
			skip = False
			for pid, fixed in roster:
				if pid == sid:
					logger.debug(tb(tabs+1) + "player is already rostered somehow")
					del sortside[0]
					skip = True
			if skip:
				tabs-=2
				continue
				
			# Step 4.2: Check that player is of matching level
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.2: Check that player is of matching level")
			member = utils.get(guildobj.members, id=int(sid))
			if Serv["settings"]["levelcapson"] == "1":		
				theirnick = ""
				if member == None:
					# Player left the guild
					theirnick = sid + " (left)"
				else:
					theirnick = member.nick
					if theirnick == None:
						theirnick = member.display_name
				level = GetCharLevel(theirnick, tabs+1)
				logger.debug(tb(tabs+1) + "Level: " + str(level))
				if type(level) == type(""):
					logger.debug(tb(tabs+1) + "Member " + theirnick + " hasn't formatted their name to show their level correctly")
					del sortside[0]
					tabs-=2
					continue	
			
				if level < 	int(GameDict["minlevel"]):
					logger.debug(tb(tabs+1) + "Character level " + str(level) + " is below minlevel " + str(GameDict["minlevel"]))
					del sortside[0]
					tabs-=2
					continue		
			
				if level > 	int(GameDict["maxlevel"]):
					logger.debug(tb(tabs+1) + "Character level " + str(level) + " is above maxlevel " + str(GameDict["maxlevel"]))
					del sortside[0]
					tabs-=2
					continue	
			
			# Step 4.3: Check that player isn't rostered in any future games
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.3: Check that player isn't rostered in any future games")
			future = Serv["players"][sid]["r"]
			maxrostersetting = Serv["settings"]["playermaxroster"]
			logger.debug(tb(tabs+1) + "maxrostersetting: " + maxrostersetting + " | future games: " + str(future))
			if len(future) >= int(maxrostersetting):
				logger.debug(tb(tabs+1) + "Has too many future games rostered")
				del sortside[0]
				tabs-=2
				continue
		
			# Step 4.4: Check that player isn't playing more games in a row than playermaxconsecutive
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.4: Check that player isn't playing more games in a row than playermaxconsecutive")
			if CheckConsecutiveRosters(Serv, sid, gid, tabs+1):
				logger.debug(tb(tabs+1) + "Would be playing too many games in a row")
				del sortside[0]
				tabs-=2
				continue
			
			# Step 4.5: Check that they're not fixed to sideline
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.5: Check that they're not fixed to sideline")
			if movefixed == False and thispl[3] == "fixed":
				logger.debug(tb(tabs+1) + "Player is fixed to sidelines")
				del sortside[0]
				tabs-=2
				continue			
	
			# Step 4.6: Check if there is a rostered player of lower priority
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 4.6: Check if there is a rostered player of lower priority")
			for rpos, rpl, rpnum, rstatus in croster:
				logger.debug(tb(tabs+1) + "checking (" + str(rpos) + " " + str(rpl) + " " + str(rpnum) + " " + str(rstatus) + ")")
				if rpnum > pnum:
					logger.debug(tb(tabs+1) + "This rostered player has worse priority than sidelined")
					if rstatus == "fixed" and movefixed == False:
						logger.debug(tb(tabs+1) + "skipping as can't move fixed")
						tabs-=2
						continue
					else:
						logger.debug(tb(tabs+1) + "Found an insert position at: " + str(rpos))
						insertpos = rpos
						break
		
			if insertpos == -1:
				logger.debug(tb(tabs+1) + "There are no rostered players with worse priority")		
				sortside.clear() # blank sortside to exit
			else:
				logger.debug(tb(tabs+1) + "Found a filling")
			tabs-=2
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of sortside loop: " + str(sortside))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Insert pos: " + str(insertpos))
	if len(sortside):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding player " + str(sortside[0]))
		thispl 	= sortside[0]
		pos		= thispl[0]
		sid		= thispl[1]
		pnum 	= thispl[2]
		status  = thispl[3]
		ele 	= [sid, status]
		GameDict["roster"].insert(insertpos, ele)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roster now: " + str(GameDict["roster"]))
		# Check if a player is being demoted
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if a player should be demoted. Roster length now: " + str(len(GameDict["roster"])) + ", mapx: " + str(maxp))
		
		while len(GameDict["roster"]) > int(maxp):
			roster 	= GameDict["roster"]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Roster in excess: " + str(len(roster) - int(maxp)))
			for rpos, (rpl, rstatus) in list(enumerate(GameDict["roster"][:]))[::-1]: # gotta enumerate, convert to list, THEN reverse it
				if len(GameDict["roster"]) <= int(maxp):
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removed enough players")
					break
				logger.debug(tb(tabs+1) + "Checking " + str(rpos) + " " + str(rpl) + " " + str(rstatus))
				if movefixed == False and rstatus == "fixed":
					logger.debug(tb(tabs+1) + "Can't move a fixed player")
					continue
				logger.debug(tb(tabs+1) + "Removing from roster")
				del GameDict["roster"][rpos]
				
				logger.debug(tb(tabs+1) + "Messaging player to advise")
				ptz = Serv["players"][rpl]["tz"]
				if ptz == "":
					ptz == GameDict["timezone"]
				if ptz == "":
					# don't why this would be the case
					logger.warning(tb(tabs+1) + "Somehow the game " + gid + " doesn't have, or I couldn't get, a timezone? function: PromoteFromSidelines. " + str(GameDict))
					ptz = "UTC"
				member = utils.get(guildobj.members, id=int(rpl))
				msg = member.mention + " NOTICE! Due to priorities, you have been demoted from the roster of game:\n" + gid + " " + GameDict["name"] + "\tStarting: " + GetGameDateTime(Serv, gid, tz=ptz, tabs=tabs+1)
				await member.send(msg)
				logger.debug(tb(tabs+1) + "Updating demoted's roster records")
				RemovePlayerGameList(Serv, rpl, gid, "r", tabs+1)
				
				logger.debug(tb(tabs+1) + "Inserting to sidelines if on")				
				if GameDict["sidelineson"] == "1" and int(maxsp) > 0: # not checking if sidelines is longer than allowed YET
					logger.debug(tb(tabs+1) + "Inserting")
					thistup = (rpl, rstatus)
					GameDict["sideline"].insert(0, thistup)
					logger.debug(tb(tabs+1) + "Updating demoted's sideline records")
					AddPlayerGameList(Serv, rpl, gid, "s", tabs+1)
					msg = member.mention + " NOTICE! You have been added to the sidelines of game:\n" + gid + " " + GameDict["name"] + "\tStarting: " + GetGameDateTime(Serv, gid, tz=ptz, tabs=tabs+1)
					await member.send(msg)
				else:
					logger.debug(tb(tabs+1) + "No sidelines on to add")		
		
		# Delete Promoted from Sideline
		logger.debug(tb(tabs+1) + "Deleting Promoted from Sideline")
		logger.debug(tb(tabs+1) + "Sidelines before: " + str(GameDict["sideline"]))

		scopy = GameDict["sideline"] 
		for num, (pid, pstatus) in list(enumerate(scopy))[::-1]:	#reversed copy	
			if sid == pid:
				logger.debug(tb(tabs+1) + "found one to delete at position: " + str(num))
				del GameDict["sideline"][num]
		logger.debug(tb(tabs+1) + "Sidelines after: " + str(GameDict["sideline"]))
		
		logger.debug(tb(tabs+1) + "Updating their records")
		RemovePlayerGameList(Serv, sid, gid, "s", tabs+1)
		AddPlayerGameList(Serv, sid, gid, "r", tabs+1)
		member = utils.get(guildobj.members, id=int(sid))
		# Need to message that player to advise they have been Rostered!
		logger.debug(tb(tabs+1) + "Messaging player to advise")
		ptz = Serv["players"][sid]["tz"]
		if ptz == "":
			ptz == GameDict["timezone"]
		msg = member.mention + " NOTICE! You have been promoted from the sidelines to the roster for game:\n" + gid + " " + GameDict["name"] + "\tStarting: " + GetGameDateTime(Serv, gid, tz=ptz, tabs=tabs+1)
		await member.send(msg)
		
		# Check that sidelines is still below limits
		logger.debug(tb(tabs+1) + "Checking that sidelines is within limits")
		slen = len(GameDict["sideline"])
		logger.debug(tb(tabs+1) + str(slen) + " of max " + str(maxsp))
		while len(GameDict["sideline"]) > int(maxsp):
			tabs+=1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sorting sidelines by priority and position")
			prios = [(spos, pl, CalcPlayerPriority(Serv, pl, tabs), fixed) for spos, (pl, fixed) in enumerate(GameDict["sideline"])]
			if Serv["settings"]["prioritieson"] == "1":
				sortside = sorted(prios, key=lambda element: (element[2], element[0]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finding lowest position player that isn't fixed")
			spos = len(sortside)-1 # end of the list
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " spos: " + str(spos))
			if movefixed == False:
				while spos >= 0 and sortside[spos][3] == "fixed":
					spos-=1 # move back one
					logger.debug(tb(tabs+2) + "Sidelined player was fixed. spos now: " + str(spos))
				if spos < 0:
					logger.debug(tb(tabs+1) + "There's no unfixed players left to remove")
					break
			logger.debug(tb(tabs+1) + "Reducing sidelines at pos: " + str(spos) + ", record: " + str(GameDict["sideline"][spos]))
			rm = sortside[spos]
			del GameDict["sideline"][rm[0]]
			RemovePlayerGameList(Serv, rm[1], gid, "s", tabs)
			member = utils.get(guildobj.members, id=int(rm[1]))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Messaging removed sidelined player to advise")
			ptz = Serv["players"][rm[1]]["tz"]
			if ptz == "":
				ptz == GameDict["timezone"]
			msg = member.mention + " NOTICE! Due to limits on sideline numbers, you have been removed from the sidelines for game:\n" + gid + " " + GameDict["name"] + "\tStarting: " + GetGameDateTime(Serv, gid, tz=ptz, tabs=tabs)
			await member.send(msg)
			tabs-=1
	else:
		logger.debug(tb(tabs+1) + "No players to add")
	
	# Check if there are even more positions to fill
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if more positions to fill")
	filled = False
	if insertpos != -1:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling PromoteFromSidelines once more")
		filled = True
		await PromoteFromSidelines(bot, Serv, gid, movefixed=movefixed, tabs=tabs) 
	else:
		logger.debug(tb(tabs+1) + "No more")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Promoted a player? " + TOGGLEFT[filled])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of PromoteFromSidelines")
	return filled

async def UpdateGameEmbeds(msg, gameid, method, tabs=0):
	""" Updates all messages saved in publishid with new embeds"""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UpdateGameEmbeds")
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
	thisgame	= Serv["games"][gameid]
	logger.debug(tb(tabs)+ "Gamedict:")
	deeplogdict(thisgame, "debug", tabs+1)
	msgcount = 0
	if method == "publish":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publishing game embed")
		emb = GetGameInfoEmbed(ctx.bot, Serv, gameid, None, tabs=tabs)
		outputchans = thisgame["publishchannels"][:]
		if thisgame["completed"] == "1":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is completed")
			if len(thisgame["completedchannels"]):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game has completedchannels: " + str(thisgame["completedchannels"]))
				outputchans = thisgame["completedchannels"][:]
			else:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No completedchannels")
				outputchans = []
		if len(outputchans):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting to publishchannel/s")
			chans = []
			for each in outputchans:
				chan = guildobj.get_channel(int(each))
				if chan not in ["", None]:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending to " + chan.name)
					try:
						mess = await chan.send(embed=emb)
					except Forbidden:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + "Couldn't publish to the channel: Don't have guild permission to")
						await ctx.send("I couldn't publish to " + chan.name + " because your Discord server doesn't allow me to")
						mess = None
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in Update Game Embeds:\n" + str(edata))						
					if mess != None and str(mess.id) not in [mid for mid, chan in thisgame["publishid"]]:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding mess.id " + str(mess.id) + " and chan.id " + str(mess.channel.id) + " to publishid")
						thisgame["publishid"].append((str(mess.id), str(mess.channel.id)))
						msgcount += 1
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " msgcount: " + str(msgcount))
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No game channels to output to. Sending to ctx")
			await ctx.send(embed=emb)
			msgcount += 1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " msgcount: " + str(msgcount))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished publishing embeds!")	
	elif method in ["update", "unpublish"]:
		logger.debug(tb(tabs) + method + "ing published embeds")
		chancopy = thisgame["publishchannels"][:]
		if thisgame["completed"] == "1" and len(thisgame["completedchannels"]):
			outputchans = thisgame["completedchannels"][:]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publishchannels: " + str(chancopy))
		emb = None
		if len(thisgame["publishid"]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Found " + str(len(thisgame["publishid"])) + " embeds: " + str(thisgame["publishid"]))
			emb = GetGameInfoEmbed(ctx.bot, Serv, gameid, None, tabs=tabs)
			pcopy = thisgame["publishid"][:]
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pcopy: " + str(pcopy))
			for num, (mid, chan) in list(enumerate(pcopy))[::-1]:
				logger.debug(tb(tabs) + str(num) + " Getting message #" + str(num) + " id: " + mid + " from channel " + str(chan))
				tabs+=1
				chanobj = ctx.bot.get_channel(int(chan))
				logger.debug(tb(tabs+1) +  "chanobj found: " + str(chanobj))
				mess = None
				if chanobj == None:
					logger.debug(tb(tabs+1) +  "No channel found? Weird. Maybe it was deleted? Gonna try getting the message direct from ctx")
					try:
						mess = await ctx.fetch_message(int(mid))
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning(tb(tabs) +  "Error finding a message id (" + str(mid) + "): " + str(edata))
						#print(edata)
						me = await ctx.bot.fetch_user(AUTHORID)
						await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Error finding a message: " + mid + " from channel " + str(chan) + " for gameid " + str(gameid) + ":\n" + str(edata) + "\nJust deleting the bad data and moving on")
						await ctx.send("There was a problem trying to find an embed message that the game was published to. Was it manually deleted by someone?")
						logger.warning('\t\t' + "Deleting this embed listing")
						del thisgame["publishid"][num]
						continue						
				else:
					logger.debug(tb(tabs+1) +  "Found the channel. Getting the message")
					mess = None
					loops = 1
					edata = None
					while mess == None and loops < 6:
						try:
							mess = await chanobj.fetch_message(int(mid))
						except (Exception, DiscordException) as e:
							logger.warning(tb(tabs+1) + "Couldn't find a message after attempt # " + str(loops))
							edata = PrintException()
							logger.warning(tb(tabs+1) + "Error finding a message id (" + str(mid) + "): " + str(edata))
							loops += 1
							await asyncio.sleep(1)
					if mess == None:
						logger.warning(tb(tabs+1) + "Still couldn't find a message after " + str(loops) + " attempts. Moving on")						
						del thisgame["publishid"][num] # deleting this weird message that couldn't be found from the record
						#print(edata)
						me = await ctx.bot.fetch_user(AUTHORID)
						await me.send("Error finding a message: " + str(edata))
						continue
				if mess != None:
					logger.info(tb(tabs+1) + "Found message! " + str(mess))
					if method == "update":
						try:
							logger.debug(tb(tabs+1) + "trying to edit message " + str(mess))
							await mess.edit(embed=emb)
							thisgame["publishid"][num] = (str(mess.id), str(mess.channel.id))
							msgcount += 1
							logger.debug(tb(tabs+1) + "msgcount: " + str(msgcount))
							logger.debug(tb(tabs+1) + "Removing from chancopy")
							while str(mess.channel.id) in chancopy:
								chancopy.remove(str(mess.channel.id))
							logger.debug(tb(tabs+1) +  "chancopy now: " + str(chancopy))
						except DiscordException as e:
							edata = PrintException()
							logger.warning(tb(tabs+1) +  "Error editing a message: " + str(edata))
							#print(edata)
							me = await ctx.bot.fetch_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Error editing a message: " + str(edata))
					else: # unpublish
						try:
							logger.debug(tb(tabs+1) +  "trying to delete message " + str(mess))
							await mess.delete()
							logger.debug(tb(tabs+1) +  "Deleting record of published message")
							msgcount += 1
							logger.debug(tb(tabs+1) + "msgcount: " + str(msgcount))
						except DiscordException as e:
							edata = PrintException()
							logger.warning(tb(tabs+1) +  "Error deleting a message: " + str(edata))
							#print(edata)
							me = await ctx.bot.fetch_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Error deleting a message: " + str(edata))
				else:
					logger.info(tb(tabs) + "Didn't find a message! But this should probably never print")
			tabs-=1
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending an embed to any remaining publishchannels: " + str(chancopy))		
		if method == "update" and thisgame["completed"] == "0" and thisgame["published"] == "1": # checking if it's completed in case someone with authority was editing completed games for some reason	
			tabs+=1
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is not completed and IS published, so posting to chancopy: " + str(chancopy))
			if emb == None: # the embed wasn't previously created above
				emb = GetGameInfoEmbed(ctx.bot, Serv, gameid, None, tabs=tabs)
			
			for each in chancopy:
				logger.info(tb(tabs) + "Sending to: " + str(each))
				chan = guildobj.get_channel(int(each))
				if chan not in ["", None]:
					logger.debug(tb(tabs+1) + "Sending to " + chan.name)
					mess = await chan.send(embed=emb)
					msgcount += 1
					if mess != None and str(mess.id) not in [mid for mid, chan in thisgame["publishid"]]:
						logger.debug(tb(tabs+1) + "Adding mess.id " + str(mess.id) + " and chan.id " + str(mess.channel.id) + " to publishid")
						thisgame["publishid"].append((str(mess.id), str(mess.channel.id)))
			tabs-=1
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished " + method + "ing embeds!")					
	if method == "unpublish":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " clearing published message ids")
		thisgame["publishid"].clear()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " publishid now: " + str(thisgame["publishid"]))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished deleting embeds!")	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Listed publishids now: " + str(thisgame["publishid"]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UpdateGameEmbeds")
	return msgcount

async def UpdateGameEmbedsBot(bot, Serv, guildobj, gameid, tabs=0):
	""" Like UpdateGameEmbeds, but only used if you don't have a ctx (loops, etc)"""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UpdateGameEmbedsBot")
	tabs += 1
	logger.debug(tb(tabs)+ "Gamedict:")
	thisgame	= Serv["games"][gameid]
	deeplogdict(thisgame, "debug", tabs+1)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating published embeds")
	chancopy = thisgame["publishchannels"][:]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publishchannels is: " + str(chancopy))
	if len(thisgame["publishid"]):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Found " + str(len(thisgame["publishid"])) + " embeds")
		emb = GetGameInfoEmbed(bot, Serv, gameid, None, tabs=tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " publishids: " + str(thisgame["publishid"]))
		pcopy = thisgame["publishid"][:] #reversed copy
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " pcopy: " + str(pcopy))
		for num, (mid, chan) in list(enumerate(pcopy))[::-1]:
			logger.debug(tb(tabs+1) + str(num) + " Getting message " + str(mid) + " from channel " + str(chan))
			chanobj = guildobj.get_channel(int(chan))
			logger.debug(tb(tabs+1) + "chanobj found: " + str(chanobj))
			mess = None
			if chanobj == None:
				logger.debug(tb(tabs+1) + "No channel found? Weird. Maybe it was deleted?")
				me = await ctx.bot.fetch_user(AUTHORID)
				await me.send("Error finding a message: " + mid + " from channel " + str(chan) + " for gameid " + str(gameid) + ":\n" + str(e) + "\nJust deleting the bad data and moving on")
				logger.warning(tb(tabs+1) + "Deleting this embed listing")
				del thisgame["publishid"][num]						
			else:
				logger.debug(tb(tabs+1) +  "Found the channel. Getting the message")
				loops = 1
				edata = None
				while mess == None and loops < 6:
					try:
						mess = await chanobj.fetch_message(int(mid))
					except (Exception, DiscordException) as e:
						logger.warning(tb(tabs+1) + "Couldn't find a message after attempt # " + str(loops))
						edata = PrintException()
						logger.warning(tb(tabs+1) + "Error finding a message id (" + str(mid) + "): " + str(edata))
						loops += 1
						await asyncio.sleep(1)

				if mess == None:
					logger.warning(tb(tabs+1) + "Still couldn't find a message after " + str(loops) + " attempts. Moving on")						
					del thisgame["publishid"][num] # deleting this weird message that couldn't be found from the record
					#print(edata)
					me = await bot.fetch_user(AUTHORID)
					await me.send("Error finding a message: " + str(edata))
					continue
				if mess != None:
					logger.info('\t\t' + "Found message! " + str(mess))
					try:
						logger.debug(tb(tabs+1) +  "trying to edit message " + str(mess))
						await mess.edit(embed=emb)
						thisgame["publishid"][num] = (str(mess.id), str(mess.channel.id))
						logger.debug(tb(tabs+1) +  "Removing from pcopy")
						while str(mess.channel.id) in chancopy:
							chancopy.remove(str(mess.channel.id))
						logger.debug(tb(tabs+1) +  "pcopy now: " + str(chancopy))
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning(tb(tabs+1) + "Error editing a message: " + str(edata))
						#print(edata)
						me = await bot.fetch_user(AUTHORID)
						await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Error editing a message: " + str(edata))
				else:
					logger.info('\t\t' + "Didn't find a message! But this should probably never print")
		
		logger.info(tb(tabs) + "Sending an embed to any remaining publishchannels: " + str(chancopy))
		for each in chancopy:
			logger.info(tb(tabs) + "Sending to: " + str(each))
			chan = guildobj.get_channel(int(each))
			if chan not in ["", None]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending to " + chan.name)
				mess = await chan.send(embed=emb)
				if mess != None and str(mess.id) not in [mid for mid, chan in thisgame["publishid"]]:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding mess.id " + str(mess.id) + " and chan.id " + str(mess.channel.id) + " to publishid")
					thisgame["publishid"].append((str(mess.id), str(mess.channel.id)))
					
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Listed publishids now: " + str(thisgame["publishid"]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UpdateGameEmbedsBot")	

def CollateUpdateMsgs(msg, gameid, group="detail", tabs=0):
	""" Gathers a list of users who need to be updated"""
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CollateUpdateMsgs")
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
	thisgame	= Serv["games"][gameid]	

	userlist = []
	if group == "detail":
		logger.debug(tb(tabs+1) + "Collating details data group")
		if thisgame["whispergmdetailupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding GM")
			GMid = thisgame["gm"]
			GM = GetMember(ctx, GMid)
			userlist.append(GM)
		if thisgame["whisperplayersdetailupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding rostered players")
			for each in thisgame["roster"]:
				logger.debug(tb(tabs+1) + "Adding player " + each[0])
				pid = each[0]
				pl = GetMember(ctx, pid)
				if pl not in ["", None]:
					userlist.append(pl)
		if thisgame["whispersidelinedetailupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding sidelined players")
			for each in thisgame["sideline"]:
				logger.debug(tb(tabs+1) + "Adding sidelined player " + each[0])
				pid = each[0]
				pl = GetMember(ctx, pid)
				if pl not in ["", None]:
					userlist.append(pl)			
	elif group == "roster":
		logger.debug(tb(tabs+1) + "Collating roster data group")
		if thisgame["whispergmrosterupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding GM")
			GMid = thisgame["gm"]
			GM = GetMember(ctx, GMid)
			userlist.append(GM)
		if thisgame["whisperplayersrosterupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding rostered players")
			for each in thisgame["roster"]:
				logger.debug(tb(tabs+1) + "Adding player " + each[0])
				pid = each[0]
				pl = GetMember(ctx, pid)
				if pl not in ["", None] and pl not in userlist:
					userlist.append(pl)
		if thisgame["whispersidelinerosterupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding sidelined players")
			for each in thisgame["sideline"]:
				logger.debug(tb(tabs+1) + "Adding sidelined player " + each[0])
				pid = each[0]
				pl = GetMember(ctx, pid)
				if pl not in ["", None] and pl not in userlist:
					userlist.append(pl)			
	elif group == "sideline":
		logger.debug(tb(tabs+1) + "Collating sideline data group")
		if thisgame["whispergmsidelineupdates"] in TOGGLEON:
			logger.debug(tb(tabs+1) + "Adding GM")
			GMid = thisgame["gm"]
			GM = GetMember(ctx, GMid)
			if GM not in userlist:
				userlist.append(GM)
	logger.debug(tb(tabs+1) + "End of CollateUpdateMsgs")
	logger.debug(tb(tabs+1) + "Users to be updated: " + str(userlist))
	return userlist
	
def AuthorityCheck(SS, authorobj, check, priv, command, subc=None, gamedict=None, tabs=0):
	""" Tests whether the author has the correct authority for this 
	Returns tuple of true/false and error message if any """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of AuthorityCheck")
	tabs += 1

	result = False
	message = authorobj.mention + " You don't have permission to use command " + command
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking Authority for command " + command)
	if priv > int(SS["settings"]["authority"][check]):		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " User doesn't have authority to use command: " + command + ", subc: " + str(subc))
	else:			
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Authority passed")
		result = True
		message = authorobj.mention + " is Authorised to use command " + command + ", subc: " + str(subc) # Not necessary, as won't look at this if result = True, but looks better in the logs
	
	if check == "gameid" and result == True: # Editing a game
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if Game is marked completed")
		if gamedict == None:
			logger.error('\t' + "ERROR. Trying to check the Set authority for a game, but no gamedict given!")		
		elif gamedict["completed"] == "1":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is complete. Checking Authority")
			authsetting2 = SS["settings"]["authority"]["editcompleted"]	# Editing COMPLETED games
			if priv > int(authsetting2):
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " User doesn't have authority to use command: " + command + ", subc: " + str(subc) + " on a game marked as complete")
				result = False
				message = authorobj.mention + " You don't have permission to use this command on a game marked as completed"	
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game is NOT complete. No further check needed")

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " result is " + str((result, message)))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of AuthorityCheck")	
	return (result, message)

def TestPlayerEligibility(Serv, gid, pid, playerdict, memberobj, team="roster", removefixed=False, tabs=0):
	""" Returns True or False on whether the player is eligible to be listed for the given game """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of TestPlayerEligibility")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid received: " + str(gid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " playerid received: " + str(pid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " removefixed: " + TOGGLEFT[removefixed])
	GameDict	= Serv["games"][gid]
	
	# Step 1: Check that player is of matching level
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1: Check that player is of matching level")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " levelcapson: " + str(Serv["settings"]["levelcapson"]))
	theirnick = ""
	if Serv["settings"]["levelcapson"] == "1":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking levels")
		theirnick = memberobj.nick
		if theirnick == None:
			theirnick = memberobj.display_name
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " theirnick: " + theirnick)	
		level = GetCharLevel(theirnick, tabs=tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " level: " + str(level))
		if type(level) == type(""):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Member " + theirnick + " hasn't formatted their name to show their level correctly")
			return (False, "Member " + theirnick + " hasn't formatted their name to show their character level correctly")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " minlevel: " + str(GameDict["minlevel"]))
		if level < 	int(GameDict["minlevel"]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Character level " + str(level) + " is below minlevel " + str(GameDict["minlevel"]))
			return (False, "Member " + theirnick + " has level " + str(level) + " is below minlevel " + str(GameDict["minlevel"]))		
	
		if level > 	int(GameDict["maxlevel"]):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Character level " + str(level) + " is below maxlevel " + str(GameDict["maxlevel"]))
			return (False, "Member " + theirnick + " has level " + str(level) + " is below maxlevel " + str(GameDict["maxlevel"]))	
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " levelcapson is OFF")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 1 Passed")
	
	# Step 2: Check that player isn't rostered in too many future games
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2: Check that player isn't rostered in too many future games")
	letter = 'r'
	maxname = "playermaxroster"
	plural = "rostered"
	if team == "sideline":
		letter = 's'
		maxname = "playermaxsideline"
		plural = "sidelined"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " letter: " + letter + ", maxname: " + maxname + ", plural: " + plural)
	future = playerdict[letter]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " future: " + str(future))
	maxallowed = Serv["settings"][maxname]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " maxallowed: " + maxallowed)
	if int(maxallowed) != -1 and len(future) > int(maxallowed):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Has too many future games rostered")
		return (False, "Member " + theirnick + " is " + plural + " for too many games (" + str(len(future)) + " of " + str(maxallowed) + " allowed by the guild)")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 2 Passed")
	
	# Step 3: Check that player isn't playing more games in a row than playermaxconsecutive
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 3: Check that player isn't playing more games in a row than playermaxconsecutive")
	if team == "roster":
		consec = CheckConsecutiveRosters(Serv, pid, gid, tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Consec: " + TOGGLEFT[consec])
		if consec:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Would be playing too many games in a row")
			return (False, "Member " + theirnick + " is rostered for too many games in a row as allowed by the guild")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Step 3 Passed")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Player is eligible")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of TestPlayerEligibility")
	return (True, "Player is eligible")

async def AuditRoster(thebot, guilddict, gameid, movefixed=False, tabs=0):
	""" Checks roster for empty spaces that can be filled from sidelines and
	if anyone in sidelines now has a better priority than a rostered person
	and if anyone has leveled up too high """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of AuditRoster")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guildid received: " + str(guilddict["GuildID"]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid received: " + str(gameid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " movefixed: " + TOGGLEFT[movefixed])
	
	# Easy access variables
	guildid		= guilddict["GuildID"]	
	guildobj 	= thebot.get_guild(int(guildid))
	gamedict	= guilddict["games"][gameid]
	serv		= guilddict
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " GameDict: ")
	logger.debug(tb(tabs) + str(gamedict))
	
	teams = ["roster", "sideline"]
	deletion = False
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking Ineligibility for gameid: " + gameid)
	for thisteam in teams:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " checking team: " + thisteam + ", list: " + str(gamedict[thisteam]))		#20112519her
		for pos, (pl, status) in list(enumerate(gamedict[thisteam][:]))[::-1]: #reversed
			logger.debug(tb(tabs+1) + "checking player: " + str(pl) + " " + str(status))
			playerdict = serv["players"][pl]
			memberobj = guildobj.get_member(int(pl))
			result = True
			if memberobj == None:
				logger.debug(tb(tabs+1) + "Player left the guild: " + pl)
				result = [False, ""]
			else:
				logger.debug(tb(tabs+1) + memberobj.display_name)
				result = TestPlayerEligibility(serv, gameid, pl, playerdict, memberobj, team=thisteam, removefixed=movefixed, tabs=tabs+1) #(Serv, gid, pid, playerdict, memberobj, team="roster", removefixed=False)
			logger.debug(tb(tabs+1) + "result: " + str(result))
			if result[0] == False and ((movefixed == True) or (movefixed == False and status.lower() == "unfixed")):
				logger.debug(tb(tabs+1) + "Telling member that they are ineligible")
				if memberobj != None: # Still in guild
					mess = memberobj.mention + " you have been removed from the " + thisteam + " for game " + gameid + " for the following reason:\n"
					try:
						await memberobj.send(mess + result[1])
					except HTTPException as e:
						edata = PrintException()
						logger.error('\t' + "There was a HTTPException error sending " + memberobj.display_name + " a message advising they are not eligible for game " + gameid)
						logger.error('\t' + str(edata))
					except Forbidden as e:
						edata = PrintException()
						logger.warning("Roster Reminder: Couldn't send message to user as was forbidden (they've probably blocked the bot):\n" + str(edata))				
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in Audit Roster:\n" + str(edata))
						if thebot.is_ready():
							me = thebot.get_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in Roster Reminder:\n" + str(edata))	
				logger.debug(tb(tabs+1) + "Removing from that list")
				RemoveFromTeam(serv, gameid, pl, team=thisteam, removefixed=movefixed, tabs=tabs+1)
				deletion = True
		logger.debug(tb(tabs+1) + "End of team " + thisteam + " check")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Promoting players for gameid: " + str(gameid))
	promote = await PromoteFromSidelines(thebot, serv, gameid, movefixed=False, tabs=tabs) #(bot, Serv, gid, movefixed=False)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking list sizes for gameid: " + gameid)
	maxes = {"roster": "maxplayers", "sideline": "maxsidelines"}
	letters = {"roster": "r", "sideline": "s"}
	demote = False
	for thisteam in teams:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " checking team: " + thisteam)
		msize = gamedict[maxes[thisteam]]
		logger.debug(tb(tabs) + thisteam + " current size: " + str(len(gamedict[thisteam])) + " of msize: " + str(msize))
		while len(gamedict[thisteam]) > int(msize): # not doing this any lower because I'm not sure how the deletions will shuffle people's positions
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Shrinking list")
			worstp = []
			for pos, (pl, status) in enumerate(gamedict[thisteam]):			
				if status != "fixed":
					pdata = (pos, pl, CalcPlayerPriority(guilddict, pl, tabs))
					worstp.append(pdata)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " worstp: " + str(worstp))
			worstp = sorted(worstp, key=lambda element: (element[2], element[0])) # sort from smallest to largest
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " worstp after sorting by priority and then position: " + str(worstp))
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting last pos: " + str(worstp[-1]))
			pos = worstp[-1][0]
			pl = worstp[-1][1]
			if thisteam == "roster":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding the player to the start of the sidelines")
				gamedict["sideline"].insert(0, (pl, "unfixed"))
				AddPlayerGameList(guilddict, pl, gameid, "s", tabs=tabs)
							
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating demoted user's game lists")
			RemovePlayerGameList(guilddict, pl, gameid, letters[thisteam], tabs=tabs)	
				
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting demoted from list")
			del gamedict[thisteam][pos]

			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting demoted user object")
			pobj = await thebot.fetch_user(int(pl))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Demoted player object: " + str(pobj))
			
			if pobj != None:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Creating demoted's output message")
				newoutput = pobj.mention + " has been removed from the " + thisteam + " for game " + gameid + " due to priorities"				
				try:
					await pobj.send(newoutput)
				except Forbidden as e:
					edata = PrintException()
					logger.warning("Roster Reminder: Couldn't send message to user as was forbidden (they've probably blocked the bot):\n" + str(edata))				
				except (Exception, DiscordException) as e:
					edata = PrintException()
					logger.warning("There was an error in Audit Roster:\n" + str(edata))
					if thebot.is_ready():
						me = thebot.get_user(AUTHORID)
						await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in Roster Reminder:\n" + str(edata))	
			demote = True
				
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating game embeds")
	if deletion or promote or demote:
		await UpdateGameEmbedsBot(thebot, serv, guildobj, gameid, tabs=tabs) #(bot, Serv, guildobj, gameid)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of AuditRoster")

async def RosterReminder(thebot, guilddict, gameid, tabs=0):
	""" Check when and if to send reminders, and does so """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of Roster Reminder for guild: " + str(guilddict["GuildID"]) + " gameid: " + str(gameid))
	tabs += 1
	
	gamedict = guilddict["games"][gameid]
	reminder = gamedict["reminderson"]
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if reminders are on")
	if reminder == "0":
		logger.debug(tb(tabs+1) + "Reminders off. End of Roster Reminder")
		return
	else:
		logger.debug(tb(tabs+1) + "Reminders on")
		
	sent = gamedict["reminders"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if reminders have already been sent")
	if len(sent.keys()):
		logger.debug(tb(tabs+1) + "Reminders already sent. End of Roster Reminder")
		return		
	else:
		logger.debug(tb(tabs+1) + "No reminders sent yet")
		
	when = gamedict["remindwhen"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if a when period is set")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " when: " + str(when))	
	if when in ["", None]:
		logger.debug(tb(tabs+1) + "No 'when' minutes set")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Roster Reminder")
		return
	else:
		logger.debug(tb(tabs+1) + "Reminder period set")
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Number of reminders to send out: " + str(len(gamedict["roster"])))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting game time")
	gtz = pytz.timezone(gamedict["timezone"])
	gametime = gamedict["datetime"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gametime: " + gtz.zone + " " + gametime)
	gt_dt = gtz.localize(datetime.strptime(gametime, TFORMAT))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gt_dt: " + str(gt_dt))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting minutes to subtract")
	subtract_td = timedelta(minutes=int(when))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting reminder time")
	rtime_dt = gt_dt - subtract_td
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " rtime_dt: " + str(rtime_dt))
	utc = pytz.timezone("UTC")
	now = datetime.now(utc) # a datetime object of now, using the game's timezone
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now: " + str(now))
	then = rtime_dt.astimezone(utc)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then: " + str(then))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if reminder time has passed")
	if now < then:
		logger.debug(tb(tabs+1) + "Not time yet")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Roster Reminder")
		return
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending reminders")
	msg = gamedict["remindermsg"]
	if msg in ["", None]:
		msg = "This is your courtesy reminder message about your upcoming game"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " msg: " + msg)
	guildname = guilddict["GuildName"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " guildname: " + guildname)
	gname = gamedict["name"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gname: " + gname)
	gdesc = gamedict["description"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gdesc: " + gdesc)
	people = gamedict["roster"][:]
	people.append((gamedict["gm"], None))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Recipients: " + str(people))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Going through list of ppl to send to")
	tabs += 1
	for pl, status in people:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Reminding pl: " + pl)
		tabs +=1
		ptz = guilddict["players"][pl]["tz"]
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " player data: " + str(guilddict["players"][pl]))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ptz before: " + str(ptz))
		if ptz in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No timezone set?")
			ptz    = str(gtz)
			ptzobj = gtz
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Converting timezone string to timezone object")
			ptzobj 	= pytz.timezone(ptz)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ptz after: " + str(ptz))		
		try:
			user = await thebot.fetch_user(int(pl))
		except:
			logger.error(tb(tabs) + "Couldn't find the user for some reason")
			edata = PrintException()
			logger.error(tb(tabs) + str(edata))
			tabs -=1
			continue
		if user == None:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " member left. skipping")
			continue
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " user: " + str(user))
		listing = user.mention + " | " + guildname + "\tgame:" + gameid + "\t " + str(ptz) + " " + str(gt_dt.astimezone(ptzobj).strftime(TFORMAT)) + "\t " + gname + "\n" + gdesc
		posting = msg + '\n' + listing
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " posting: " + posting)
		mid = None
		try:
			mid = await user.send(posting)
		except Forbidden as e:
			edata = PrintException()
			logger.warning("Roster Reminder: Couldn't send message to user as was forbidden (they've probably blocked the bot):\n" + str(edata))				
		except (Exception, DiscordException) as e:
			edata = PrintException()
			logger.warning("There was an error in Roster Reminder:\n" + str(edata))
			if thebot.is_ready():
				me = thebot.get_user(AUTHORID)
				await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in Roster Reminder:\n" + str(edata))	
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding to reminders: " + str(mid))
		gamedict["reminders"][pl] = str(mid)
		tabs -=1
	tabs -=1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Roster Reminder")
			
def NewgameChainCommands(thebot, guilddict, gameid, tabs=0):
	""" Check when and if to send reminders, and does so """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of NewgameChainCommands for guild: " + str(guilddict["GuildID"]) + " gameid: " + str(gameid))
	tabs += 1
	
	gamedict = guilddict["games"][gameid]	
	
	dataorder = ["name", "duration", "description", "minlevel", "maxlevel", "textchannel", "voicechannel", "link", "publishchannels"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dataorder: " + str(dataorder))
	phrase = ""
	for each in dataorder:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking " + each)
		if StrOrUnset(gamedict[each]) == "unset":
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Setting is unset")
			if guilddict["settings"]["levelcapson"] == "0" and each in ["minlevel", "maxlevel"]:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " levelcaps is off, so just setting minlevel to 1 and maxlevel to 20 and skipping this step")
				if each == "minlevel":
					gamedict[each] = "1"
				else:
					gamedict[each] = "20"
				continue
			phrase += "\nNext command:\n```!rb " + gameid + " " + each + "```"
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " phrase: " + phrase)
			return phrase
	
	phrase = "Review your game embed:\n"
	phrase += "```!rb " + gameid + "\n```"
	phrase += "If you are satisfied with the settings:\n"
	phrase += "```!rb " + gameid + " published true```"
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " phrase: " + phrase)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of NewgameChainCommands")
	return phrase

async def UpdateConnectionStatus(newmsg, bot, tabs=0):
	""" Checks if there is an announcements channel and publishes/updates connection message """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UpdateConnectionStatus")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " newmsg: " + newmsg)
	global MAINTENANCE
	
	if MAINTENANCE: # If in maintenance, don't update connection statuses
		pass
	else:
		for guildobj in bot.guilds:
			gid = guildobj.id
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking guild: " + str(gid) + " " + guildobj.name)
			tabs += 1
			if gid not in Dserver.Dserver.AllDservers.keys():
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gid not in my recorded guilds for some reason?")
				continue
			
			guilddict = Dserver.Dserver.AllDservers[gid]	
			gac = guilddict["settings"]["botannouncechannel"][:] # a copy
			mids = guilddict["settings"]["connectionmsgid"][:] # a copy
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gac: " + str(gac))
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " mids: " + str(mids))
			
			# Edit existing messages
			for num, (mid, cid) in list(enumerate(mids))[::-1]: # checking bottom to top
				logger.debug(tb(tabs+1) + "Checking mid: " + str(mid) + " cid: " + str(cid))
				logger.debug(tb(tabs+2) + "Getting chanobj")
				chanobj = guildobj.get_channel(int(cid))
				logger.debug(tb(tabs+2) + "chanobj: " + str(chanobj) + ", " + chanobj.mention)
				logger.debug(tb(tabs+2) + "Last message id: " + str(chanobj.last_message_id))
				messobj = None
				if chanobj == None:
					logger.debug(tb(tabs+2) + "Couldn't find a matching channel. Perhaps it was deleted?")
					del guilddict["settings"]["connectionmsgid"][num]
				else:
					logger.debug(tb(tabs+2) + "Getting messobj")
					try:
						messobj = await chanobj.fetch_message(int(mid))
						logger.debug(tb(tabs+2) + "messobj: " + str(messobj))
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.debug(tb(tabs+2) + "Couldn't find a matching message. Perhaps it was deleted?")
						logger.debug(tb(tabs+2) + str(edata))
						del guilddict["settings"]["connectionmsgid"][num]
						logger.debug(tb(tabs+2) + "connectionmsgid now: " + str(guilddict["settings"]["connectionmsgid"]))
						continue
					
					if messobj.content == newmsg:
						logger.debug(tb(tabs+2) + "Same content. Moving on")
						while cid in gac:
							logger.debug(tb(tabs+2) + "Removing this channel from the list of channels to check")
							gac.remove(cid)
							logger.debug(tb(tabs+2) + "gac now: " + str(gac))
						continue
					
					logger.debug(tb(tabs+2) + "Deleting the message")
					await messobj.delete()
					logger.debug(tb(tabs+2) + "Deleting the record")
					del guilddict["settings"]["connectionmsgid"][num]
					logger.debug(tb(tabs+2) + "Sending new message")
					messobj = await chanobj.send(content=newmsg)
					logger.debug(tb(tabs+2) + "Adding record in connectionmsgid")					
					guilddict["settings"]["connectionmsgid"].append((str(messobj.id), str(chanobj.id)))
					logger.debug(tb(tabs+2) + "connectionmsgid now: " + str(guilddict["settings"]["connectionmsgid"]))
					while cid in gac:
						logger.debug(tb(tabs+2) + "Removing this channel from the list of channels to check")
						gac.remove(cid)
						logger.debug(tb(tabs+2) + "gac now: " + str(gac))
				logger.debug(tb(tabs+2) + "End of this message check")
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publishing to remaining botannouncechannels: " + str(gac))
			for num, cid in list(enumerate(gac))[::-1]:
				logger.debug(tb(tabs+1) + "Publishing to cid: " + cid)
				chanobj = guildobj.get_channel(int(cid))
				if chanobj == None:
					logger.debug(tb(tabs+2) + "Couldn't find a matching channel. Perhaps it was deleted?")
					del guilddict["settings"]["botannouncechannel"][num]
					logger.debug(tb(tabs+2) + "botannouncechannel now: " + str(guilddict["settings"]["botannouncechannel"]))
				else:
					thismess = await chanobj.send(content=newmsg)
					logger.debug(tb(tabs+2) + "New message id: " + str(thismess.id))
					guilddict["settings"]["connectionmsgid"].append((str(thismess.id), cid))
					logger.debug(tb(tabs+2) + "connectionmsgid now: " + str(guilddict["settings"]["connectionmsgid"]))
				logger.debug(tb(tabs+2) + "End of sending to channel")
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of Guild Update")
			tabs -= 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End UpdateConnectionStatus")		

def SetNextPriorityReset(guilddict, giventz, dtstr, daysfromnow=0, tabs=0):
	""" Takes a datetime and updates NextPriorityReset """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of SetNextPriorityReset")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild: " + str(guilddict["GuildID"]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " giventz: " + str(giventz))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dtstr: " + str(dtstr))
	message = ""
	currentutc = guilddict["settings"]["nextpriorityreset"]
	currentconverted = ""
	if giventz.lower() != "utc" and dtstr not in ["", None]:
		currentconverted = ConvertTimezone("UTC", currentutc, giventz, fromformat=TFORMAT, toformat=TFORMAT, tabs=tabs)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " currentconverted: " + str(currentconverted))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Determining if editing a dt or calculating one")
	if daysfromnow:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calculating one. Adding " + str(daysfromnow) + " days to now")
		add_td = timedelta(days=daysfromnow)
		logger.debug(tb(tabs+1) + "add_td: " + str(add_td))
		utc = pytz.timezone("UTC")
		now = datetime.now(utc) # a datetime object of now
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now: " + str(now))
		then = now + add_td
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then: " + str(then))
		then_str = then.strftime(TFORMAT)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then_str: " + str(then_str))
		guilddict["settings"]["nextpriorityreset"] = then_str
		# No output returned if just adding days to now
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Editing one")
		newconverted = ConvertTimezone(giventz, dtstr, "UTC", fromformat=TFORMAT, toformat=TFORMAT, tabs=tabs)
		if type(newconverted) != type(""):
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Got a conversion error")		
			message = DTERROR
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking that given time is in the future")
			utc = pytz.timezone("UTC")
			now = datetime.now(utc) # a datetime object of now		
			then = utc.localize(datetime.strptime(newconverted, TFORMAT))		
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then: " + str(then))
			if now >= then:
				logger.debug(tb(tabs+1) + "Reminder time isn't in the future")
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of GSPriorityReset")
				message = "Please provide a reset time set in the future. If you would like to turn off automatic resets, use: \n"
				message += "!rb settings priorityresetfreq 0"
			else:
				guilddict["settings"]["nextpriorityreset"] = newconverted
				message = "nextpriorityreset was " + str(giventz) + " " + str(currentconverted) + " and is now " + str(giventz) + " " + str(dtstr)
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " message: " + message)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of SetNextPriorityReset")
	return message
	
def ResetPlayerPriorities(pid, playerdict, tabs=0):
	""" Moves p to l and clears gp """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ResetPlayerPriorities for pid: " + str(pid))
	tabs+=1

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Before: " + str(playerdict))
	playerdict["l"] = playerdict["p"][:] #copying played to last week
	playerdict["p"].clear() #emptying played
	playerdict["gp"].clear() #emptying GM Played
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " After: " + str(playerdict))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of ResetPlayerPriorities")

def UnResetPlayerPriorities(pid, playerdict, tabs=0):
	""" Moves l to p  """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UnResetPlayerPriorities for pid: " + str(pid))
	tabs+=1

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Before: " + str(playerdict))
	playerdict["p"] = playerdict["l"][:] #copying played to last week
	playerdict["l"].clear() #emptying played
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " After: " + str(playerdict))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UnResetPlayerPriorities")
	
async def AutomatedPriorityReset(thebot, guilddict, tabs=0):
	""" Checks if Priorities are due to be reset and does it """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of AutomatedPriorityReset")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Guild: " + str(guilddict["GuildID"]))
	resetfreq = guilddict["settings"]["priorityresetfreq"]
	nextreset = guilddict["settings"]["nextpriorityreset"]
		
	if resetfreq == "0":
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No reset freq set")
		return
	if nextreset in ["", None]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No reset date time set")
		return
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if date has passed")	
	utc = pytz.timezone("UTC")
	nextresetdt = datetime.strptime(nextreset, TFORMAT)
	nextresetdt = nextresetdt.astimezone(utc)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " nextresetdt: " + str(nextresetdt))
	
	if IsDateTimePassed(nextresetdt, tabs):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " time has passed")
		SetNextPriorityReset(guilddict, "UTC", "", daysfromnow=StrToNumber(resetfreq, tabs=tabs), tabs=tabs)
		for pid, data in guilddict["players"].items():
			logger.debug(tb(tabs+1) + "Resetting pid: " + str(pid))
			ResetPlayerPriorities(pid, data, tabs+1)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Finished with players")
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Publishing the message, if there is one")
		resetmsg  	= guilddict["settings"]["priorityresetmsg"]
		chans 		= guilddict["settings"]["botannouncechannel"]
		if resetmsg in ["", None]:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No reset message set for some reason")
		elif len(chans) == 0:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No botannouncechannel set")
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending announcement")
			gid = guilddict["GuildID"]		
			for cid in chans:
				logger.debug(tb(tabs+1) + "cid: " + str(cid))
				thischan = None
				try:
					thischan = thebot.get_channel(int(cid))
					logger.debug(tb(tabs+1) + "chan found: " + str(thischan))
				except:
					logger.debug(tb(tabs+1) + "Couldn't find this channel?")
					edata = PrintException()
					print(edata)
					continue
				try:
					mess = await thischan.send(resetmsg)
				except:
					logger.debug(tb(tabs+1) + "Couldn't send the message for some reason?")
					edata = PrintException()
					print(edata)
					continue		
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Time hasn't passed yet")
				
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of AutomatedPriorityReset")
	return

def CheckAgeOfCompleted(guilddata, gameid, gamedata, tabs):
	""" Checks if a completed game has passed DELETECOMPLETEDGAMES """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of CheckAgeOfCompleted")
	tabs += 1
	result = False
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " guilddata: " + str(guilddata["GuildID"]))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid: " + str(gameid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " DELETECOMPLETEDGAMES: " + str(DELETECOMPLETEDGAMES))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting game dt in UTC")
	dt = GetGameDateTime(guilddata, gameid, tz="UTC", tformat=TFORMAT, tabs=tabs)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dt: " + str(dt))

	add_td = timedelta(days=DELETECOMPLETEDGAMES)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " add_td: " + str(add_td))
	dt_utc = datetime.strptime(dt[4:], TDFORMAT)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dt_utc: " + str(dt_utc))
	then = dt_utc + add_td
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " then: " + str(then))
	result = IsDateTimePassed(then, tabs)
				
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " result: " + TOGGLEFT[result])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of CheckAgeOfCompleted")
	return result

def UpdateActiveGames(guilddata, gameid, gamedata, tabs):
	""" Checks if given game should be added to or removed from ActiveGames list """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of UpdateActiveGames")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid: " + str(gameid))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gamedata: " + str(gamedata))
	
	if gameid in guilddata["activegames"] and gameid not in guilddata["games"].keys():
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Game was deleted from games but not activegames")
		while gameid in guilddata["activegames"]:
			guilddata["activegames"].remove(gameid)		
	elif gamedata["completed"] == "0" and gamedata["published"] == "1" and gameid not in guilddata["activegames"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Adding game " + gameid + " to activegames")
		guilddata["activegames"].append(gameid)
	elif gamedata["completed"] == "1" or gamedata["published"] == "0" and gameid in guilddata["activegames"]:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Removing game " + gameid + " from activegames")
		while gameid in guilddata["activegames"]:
			guilddata["activegames"].remove(gameid)
	else:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No update required")
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of UpdateActiveGames")
	return