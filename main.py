#!/usr/bin/env python3
#testing things again tewtgewewt
from disctoken import TOKEN, MAINTENANCE
import inspect
import config
from config import *
import random
import requests
import time
import asyncio
import discord
intents = discord.Intents.default()
intents.members = True
import sys
from discord.ext.commands import Bot, check, is_owner, Cog
from discord import Game, Status, DiscordException, Forbidden
from discord.ext import tasks

from Dserver import *
from Functions import StartHere, DirectMessage
from Commands import SS, logger
from InternalFuncs import AuditRoster, RosterReminder, UpdateConnectionStatus, AutomatedPriorityReset, CheckAgeOfCompleted

bot = Bot(command_prefix=BOT_PREFIX, intents=intents)

Dserver = Dserver()
Dserver.ReadInDservers()

conmsg 		= None # store time of connection to send me as DM
disconmsg	= None
resumemsg	= None

BotClosing = False

SuspendAudit = []

@bot.event
async def on_connect():
	logger.info(" Bot has connected")
	uptimecon()
	global conmsg
	conmsg = updateNOW()

@bot.event
async def on_resumed():
	logger.info("Bot has resumed")
	uptimeresume()
	global resumemsg
	resumemsg = updateNOW()

@bot.event
async def on_disconnect():
	global BotClosing
	if not BotClosing: logger.warning("Bot has disconnected (\"This could happen either through the internet being disconnected, explicit calls to logout, or Discord terminating the connection one way or the other.\"")
	global disconmsg
	disconmsg = updateNOW()
	uptimediscon()

@bot.event
async def on_ready():
	tabs = 0
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of on_ready")
	tabs += 1
	global AUTHORID
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " AUTHORID: " + str(AUTHORID))
	me = await bot.fetch_user(AUTHORID)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " me: " + str(me))
	if MAINTENANCE:
		await bot.change_presence(status=Status.invisible)
	else:
		await bot.change_presence(activity=discord.CustomActivity(name="!rb", state="!rb", details="!rb for more info"))
	
	try:
		print("READY! Logged in as " + bot.user.name)
		global disconmsg, conmsg, resumemsg, BADSTART, LASTRUN
		
		if concount == 1 and conmsg == None:
			logger.warning("Program was just (re)started")
			await me.send("Bot just started")			
		if BADSTART:
			logger.warning("Bot wasn't shut down properly")
			await me.send("Bot wasn't shut down properly last time. Last run: " + LASTRUN)
			BADSTART = False
		if disconmsg != None:
			await me.send("Bot was DISconnected at " + disconmsg)
			disconmsg = None	
		if resumemsg != None:
			await me.send("Bot resumed at " + resumemsg)
			resumemsg = None
		elif conmsg != None:
			await me.send("Bot connected at " + conmsg)
			conmsg = None		
		await me.send("Bot is ready. Maintenance mode: " + TOGGLEFT[MAINTENANCE])
		await UpdateConnectionStatus("RosterBot is online!", bot, tabs)  # publish connection to all guilds
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of on_ready")
	except (Exception, DiscordException) as e:
		edata = PrintException()
		logger.warning(('\t' * tabs) + "Error in on_ready(): " + edata)	
		await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Error in on_ready(): " + edata)
		print("Error in on_ready(): " + edata)
	# await asyncio.sleep(70)
	# BotClosing = True		
	# Loopies.cancel_all()	
	# print("Bot Closed at " + updateNOW())
	# print("Msg: " + "offlinemsg")
	# Dserver.WriteOutDservers()
	# await clearlogs(bot, lastsend=True) # send me the last logs
	# await bot.logout()
	# logging.shutdown()
	# uptimeclose()	
	
async def clearlogs(thisbot, mbsize=config.FILEDUMPSIZE, lastsend=False, wait=True, tabs=0):
	""" Checks, copies, sends and clears log files """
	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of clearlogs")
	tabs += 1
	files = clearfile(mbsize, lastsend, tabs)
	global AUTHORID
	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Files: " + str(files))	
	for thisfile in files:
		if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending file: " + str(thisfile))
		tabs += 1
		me = None
		loops = 0
		if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Getting me as a user")
		while me == None and loops < 5:
			try:
				if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Try #" + str(loops))
				if thisbot.is_ready():
					me = thisbot.get_user(AUTHORID)
			except Exception:
				if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't find me. Waiting a sec before trying again")
				me = None
				await asyncio.sleep(1)
				loops += 1
		if me == None:
			if not lastsend: logger.warning(tb(tabs) + "main.clearlogs: Still couldn't find me as a user for some reason?")
		else:
			if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Found me. Sending me the file")
			if type(thisfile) == type("") and thisfile[:7] == "Warning":
				ftype = thisfile[7:]
				try:
					if thisbot.is_ready():
						await me.send("WARNING!!! The " + ftype + " is too big to send to you!")
				except (Exception, DiscordException) as e:
					if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't warn me a big file")
					edata = PrintException()
					print("There was an error in clearlogs sending you " + str(thisfile) + "\n" + str(edata))					
			else:
				try:
					if thisbot.is_ready():
						await me.send("Sending you this log file!"  + str(thisfile))
					fp = discord.File(thisfile)
					if thisbot.is_ready():
						await me.send(file=fp)
					if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Testing to see if the file should be deleted after sending")
					if "Dserver".lower() not in str(thisfile).lower() and MAINTENANCE == False:
						if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting the file")
						deletefiles([thisfile], lastsend, tabs)
				except (Exception, DiscordException) as e:
					edata = PrintException()
					if not lastsend: logger.warning("There was an error in clearlogs sending you " + str(thisfile) + "\n" + str(edata))
					print("There was an error in clearlogs sending you " + str(thisfile) + "\n" + str(edata))
					await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in clearlogs sending you "  + str(thisfile) + "\n" + str(edata))
		tabs -= 1
	# if wait:
	# 	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Pausing clearlogs loop")
	# 	LOGCLEARFREQ = 60 # How often to check the logs to clear them
	# 	await asyncio.sleep(LOGCLEARFREQ) # at least 1 second apart, at most 60 sec for 1 guild
	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of clearlogs")

class MyLoops(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.update_servers.start()
		self.clean_games.start()
		self.clear_logs.start()
		self.ProcPriorityResets.start()
		self.delete_old_games.start()
		
	def cancel_all(self):
		self.update_servers.cancel()
		self.clean_games.cancel()
		self.clear_logs.cancel()
		self.ProcPriorityResets.cancel()
		self.delete_old_games.cancel()

	@tasks.loop()
	async def update_servers(self):
		tabs = 0
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of update_servers")
		tabs += 1
		await self.bot.wait_until_ready()
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Bot is ready")
		while not self.bot.is_closed():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Updating Server Data")
			try:
				Dserver.CheckInvitedServers(self.bot)
				Dserver.WriteOutDservers()
			except (Exception, DiscordException) as e:
				edata = PrintException()
				logger.warning("There was an error in update_servers:\n" + str(edata))
				print("There was an error in update_servers:\n" + str(edata))
				me = self.bot.get_user(AUTHORID)
				await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in update_servers:\n"  + str(edata))
			await asyncio.sleep(UPDATEFREQ)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of update_servers")

	@tasks.loop()
	async def clean_games(self):
		""" checks that best priority players are in games """
		global SuspendAudit
		tabs = 0
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of clean_games")
		tabs += 1
		await self.bot.wait_until_ready()
		CLEANFREQ = 120 # Number of seconds between cleans of all guild games	
		while not self.bot.is_closed():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " clean_games Loop start")
			tabs += 1
			numgames = 0
			for guildid, gdata in Dserver.AllDservers.items():
				numgames += len(gdata["games"])
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " numgames = " + str(numgames))
			timer = max(CLEANFREQ/numgames, 1)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " timer: " + str(timer))
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " number of guilds: " + str(len(Dserver.AllDservers)))
			for guildid, gdata in Dserver.AllDservers.items():
				await self.bot.wait_until_ready()
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " start of clean_games loop for guild: " + str(guildid))
				tabs += 1
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Num of games to check: " + str(len(gdata["games"])))
				for gameid in gdata["activegames"]:
					gamedata = gdata["games"][gameid]
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " cleaning gameid: " + gameid)
					
					if gameid == "default":
						continue
					tabs += 1
						
					if gamedata["completed"] == "1" or gamedata["published"] == "0":
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " skipping as it is completed or unpublished")
						tabs -= 1
						continue
					
					try:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling AuditRoster")					
						while guildid in SuspendAudit:
							pass						
						await AuditRoster(self.bot, gdata, gameid, movefixed=False, tabs=tabs)
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in clean_games:\n" + str(edata))
						print("There was an error in clean_games:\n" + str(edata))
						if self.bot.is_ready():
							me = self.bot.get_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in clean_games:\n" + str(edata))					
					try:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling RosterReminder")
						await RosterReminder(self.bot, gdata, gameid, tabs=tabs)
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in clean_games:\n" + str(edata))
						print("There was an error in clean_games:\n" + str(edata))
						if self.bot.is_ready():
							me = self.bot.get_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in clean_games:\n" + str(edata))	
					
					# clear the logs in case they're really big after that
					try:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Calling clearlogs within clean_games")
						if self.bot.is_ready():
							await clearlogs(self.bot, wait=False, tabs=tabs)
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in clean_games | clearlogs:\n" + str(edata))
						print("There was an error in clean_games | clearlogs:\n" + str(edata))
						if self.bot.is_ready():
							me = self.bot.get_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in clean_games | clearlogs:\n" + str(edata))
						
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sleeping for " + str(timer) + " seconds")
					await asyncio.sleep(timer) # at least 1 second apart, at most 60 sec for 1 guild
					
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of clean for gameid: " + str(gameid))
					tabs -= 1
					
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of guild clean: " + str(guildid))
				tabs -= 1
				
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of this clean_games loop")
			tabs -= 1
	
	@tasks.loop()
	async def clear_logs(self):
		tabs = 0
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of clear_logs task loop")
		await clearlogs(self.bot)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Pausing clearlogs loop")
		LOGCLEARFREQ = 60 # How often to check the logs to clear them. 3600 = once an hour
		await asyncio.sleep(LOGCLEARFREQ) # at least 1 second apart, at most 60 sec for 1 guild
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of clear_logs task loop")
	
	@tasks.loop()
	async def ProcPriorityResets(self):
		tabs = 0
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of ProcPriorityResets")
		tabs += 1	
		await self.bot.wait_until_ready()
		CHECKFREQ = 59 # Number of seconds between checking priority resets
		while not self.bot.is_closed():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " ProcPriorityResets Loop start")
			numg = len(Dserver.AllDservers)
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " numg: " + str(numg))
			for guildid, gdata in Dserver.AllDservers.items():
				await self.bot.wait_until_ready()
				logger.debug(tb(tabs+1) + "guild: " + str(guildid))				
				try:
					logger.debug(tb(tabs+1) + "Calling AutomatedPriorityReset")
					await AutomatedPriorityReset(self.bot, gdata, tabs+1)
				except (Exception, DiscordException) as e:
					edata = PrintException()
					logger.warning("There was an error in ProcPriorityResets:\n" + str(edata))
					print("There was an error in ProcPriorityResets:\n" + str(edata))
					me = self.bot.get_user(AUTHORID)
					await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in ProcPriorityResets:\n" + str(edata))
				logger.debug(tb(tabs+2) + "End of processing automated priorities for " + str(guildid))
				timer = max(CHECKFREQ/len(Dserver.AllDservers), 1)
				logger.debug(tb(tabs+2) + "timer: " + str(timer))				
				await asyncio.sleep(timer) # at least 1 second apart, at most 59 sec for 1 guild

	@tasks.loop()
	async def delete_old_games(self):
		""" checks if games have passed deletion timeframe """
		global SuspendAudit
		tabs = 0
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of delete_old_games")
		tabs += 1
		await self.bot.wait_until_ready()
		CLEANFREQ = 86400 # Number of seconds in a day
		while not self.bot.is_closed():
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " delete_old_games Loop start")
			tabs += 1
			numgames = 0
			for guildid, gdata in Dserver.AllDservers.items():
				numgames += len(gdata["games"])
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " numgames = " + str(numgames))
			timer = CLEANFREQ/numgames
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " timer: " + str(timer))
			
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " number of guilds: " + str(len(Dserver.AllDservers)))
			for guildid, gdata in Dserver.AllDservers.items():
				await self.bot.wait_until_ready()
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " start of delete_old_games loop for guild: " + str(guildid))
				tabs += 1
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Num of games to check: " + str(len(gdata["games"])))
				gcopy = [gameid for gameid in gdata["games"].keys()] # [:] won't work. A copy so that the original list can have deletions without affecting the loop
				for gameid in gcopy:
					await asyncio.sleep(timer) # starting with the wait
					
					gamedata = gdata["games"][gameid]
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " checking gameid: " + gameid)
					
					if gameid == "default":
						continue
					tabs += 1
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking if it should be deleted")
					passed = False
					try:
						passed = CheckAgeOfCompleted(gdata, gameid, gamedata, tabs)
					except (Exception, DiscordException) as e:
						edata = PrintException()
						logger.warning("There was an error in CheckAgeOfCompleted:\n" + str(edata))
						print("There was an error in CheckAgeOfCompleted:\n" + str(edata))
						if self.bot.is_ready():
							me = self.bot.get_user(AUTHORID)
							await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an error in CheckAgeOfCompleted:\n" + str(edata))	
					
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " passed: " + TOGGLEFT[passed])
					if passed:
						logger.debug(tb(tabs) + gamedata["datetime"] + " has passed by more than " + str(DELETECOMPLETEDGAMES) + " days")
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " deleting gameid: " + str(gameid))
						
						#UpdateGameEmbedsBot(bot, gdata, gdata, gameid, tabs)
						del gdata["games"][gameid]
						UpdateActiveGames(gdata, gameid, gamedata, tabs+1)
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Num of games now: " + str(len(gdata["games"])))
						tabs -= 1
						continue
					else:
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " gameid " + str(gameid) + " is still within " + str(DELETECOMPLETEDGAMES) + " timeframe. Not deleting")

Loopies = MyLoops(bot)
			
# Close the bot
@bot.command(aliases=["quit"])
@check(is_owner())
async def close(ctx, offlinemsg, tabs=0):
	logger.warning(tb(tabs) + "Bot Shutting Down")
	tabs += 1
	BotClosing = True
	try:
		await UpdateConnectionStatus("RosterBot is offline." + " " + offlinemsg, bot, tabs) # publish connection to all guilds		
		Loopies.cancel_all()	
		print("Bot Closed at " + updateNOW())
		print("Msg: " + offlinemsg)
		Dserver.WriteOutDservers(tabs)
		logging.shutdown()
		await clearlogs(bot, lastsend=True, tabs=tabs) # send me the last logs
		await bot.logout()	
		uptimeclose()
	except (Exception, DiscordException) as e:
		edata = PrintException()
		print("Error in shutdown: " + str(edata))
	sys.exit(0)
	
@bot.command(aliases=["rb"])
async def roster(ctx):
	tabs = 0
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of roster")
	tabs += 1
	# Ignore if it was the bot speaking for any reason	
	if ctx.message.author == bot.user.name:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Ignoring message to self")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of roster")
		return

	msg = {}
	# Separate the message into arguments
	uargs = ctx.message.content.split()
	if "!roster" in uargs:
		uargs.remove("!roster")
	elif "!rb" in uargs:
		uargs.remove("!rb")
	msg["uargs"] = uargs
	msg["numargs"] = len(uargs) # number of words given, not counting !roster
	
	global MAINTENANCE, FILEDUMPSIZE
	# checking for my close command
	
	#telemenar = 280807972668571648
	permitted = [g.owner_id for g in ctx.bot.guilds] 
	permitted.append(AUTHORID)

	if ctx.message.author.id in permitted and len(uargs):
		logger.warning(('\t' * tabs) + "Message from permitted person: " + ctx.message.author.display_name)
		sender = ctx.message.author		
		if uargs[0] in ["logs", "log"]:
			logger.warning(('\t' * tabs) + "Calling logs")
			me = await ctx.bot.fetch_user(AUTHORID)
			if ctx.message.author.id == AUTHORID and len(uargs) == 2 and IsNumber(uargs[1], tabs=tabs): # Chaning 
				logger.warning(('\t' * tabs) + "Changing filedumpsize from " + str(FILEDUMPSIZE) + " to " + uargs[1])				
				if IsInt(uargs[1], tabs=tabs):
					logger.warning(('\t' * tabs) + "Changing to int")
					FILEDUMPSIZE = int(uargs[1])
				else:
					logger.warning(('\t' * tabs) + "Changing to float")
					FILEDUMPSIZE = float(uargs[1])
				logger.warning(('\t' * tabs) + "filedumpsize now: " + str(FILEDUMPSIZE))
				logger.warning(('\t' * tabs) + "End of changing filedumpsize")
				await ctx.send("Changing filedumpsize from " + str(FILEDUMPSIZE) + " to " + uargs[1])
				await clearlogs(ctx.bot, mbsize=FILEDUMPSIZE, tabs=tabs)
				return
			else:
				logger.warning(('\t' * tabs) + "Requested logs for reason.")
				reply = "Sending logs to Bot author. Thanking-you!"
				if len(uargs) > 1:
					logger.warning(('\t' * tabs) + " ".join(uargs[1:]))
					reply += "\nReason: " + " ".join(uargs[1:])
				await ctx.send(reply)
				await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Logs sent by " + ctx.message.author.mention + " to report a bug: " + " ".join(uargs[1:]))
				await clearlogs(ctx.bot, mbsize=0, tabs=tabs)
				return
		elif ctx.message.author.id == AUTHORID and uargs[0].lower() in ["exit", "quit", "close"]:
			logger.warning(('\t' * tabs) + "I have called the quit bot command")
			print("Closing the bot")
			offlinemsg = ""
			if len(uargs) > 1:
				offlinemsg = " ".join(uargs[1:])
			await ctx.send("Closing the bot. \"" + offlinemsg + "\"")
			await sender.send("Closing the bot. \"" + offlinemsg + "\"")
			try:
				await close(ctx, offlinemsg)
				return
			except:
				return
		elif ctx.message.author.id == AUTHORID and uargs[0].lower() in ["maint", "maintenance"]:
			logger.warning(('\t' * tabs) + "I have asked to switch into maintenance mode")
			print("Switching Maintenance modes")
			if len(uargs) <= 1: # not enough arguments
				return
			if uargs[1].lower() == "true":
				offlinemsg = ""
				if len(uargs) >= 2:
					offlinemsg = " ".join(uargs[2:])
				await UpdateConnectionStatus("RosterBot is offline. " + offlinemsg, bot, tabs)
				MAINTENANCE = True
				await ctx.send("Entered maintenance mode. \"" + offlinemsg + "\". MAINTENANCE: " + TOGGLEFT[MAINTENANCE])
				await sender.send("Entered maintenance mode. \"" + offlinemsg + "\". MAINTENANCE: " + TOGGLEFT[MAINTENANCE])
				await clearlogs(ctx.bot, mbsize=0, tabs=tabs)
				return
			elif uargs[1].lower() == "false":
				MAINTENANCE = False			
				await ctx.send("RosterBot is online! MAINTENANCE: " + TOGGLEFT[MAINTENANCE])
				await sender.send("RosterBot is online! MAINTENANCE: " + TOGGLEFT[MAINTENANCE])
				await UpdateConnectionStatus("RosterBot is online!", bot, tabs)
				return
			else:
				return		

	# Use this for locking out users during downtime
	if MAINTENANCE and ctx.message.author.id != AUTHORID: 
		await ctx.send("The Bot is down for maintenance. Thanks for your patience!")
		return
	
	if isinstance(ctx.message.channel, discord.DMChannel): # Needs to be before it tries getting all the impossible guild data
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Received a DM")
		output = await DirectMessage(None, tabs)
		
		if output[0] not in ["", None] and output[1] not in ["", None]:
			await output[0].send(output[1])
		return
		
	#get all the data needed and package it

	msg["guild"] 		= ctx.message.guild
	msg["serverdata"] 	= Dserver.AllDservers[ctx.message.guild.id]
	msg["ss"]			= msg["serverdata"] # stripping the !roster part
	msg["ac"]			= Commands.AC # stripping the !roster part
	msg["author"] 		= ctx.message.author
	msg["ctx"] 			= ctx
		
	# Send to the Bot Functions for processing
	gid = str(ctx.message.guild.id)
	global SuspendAudit
	SuspendAudit.append(gid)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " SuspendAudit before: " + str(SuspendAudit))
	try:
		output = await StartHere(msg)
	except Forbidden:
		logger.warning(('\t' * tabs) + "Can't send to someone that has blocked me")
	except (Exception, DiscordException) as e:
		edata = PrintException()
		print(edata)
		logger.warning(('\t' * tabs) + "There was an Error from StartHere!\n" + str(edata))
		me = await ctx.bot.fetch_user(AUTHORID)
		await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was an Error from StartHere!\n" + str(edata))
		await clearlogs(ctx.bot, mbsize=0, tabs=tabs)
		if gid in SuspendAudit:
			SuspendAudit.remove(gid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " SuspendAudit after: " + str(SuspendAudit))
	else:
		if gid in SuspendAudit:
				SuspendAudit.remove(gid)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " SuspendAudit after: " + str(SuspendAudit))
		
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " output: " + str(output))
		
		try:
			if type(output[1]) == discord.Embed:
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Printing an embed")
				await output[0].send(embed=output[1])
			elif output[1] == "List of embeds":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Outputting published game embeds")
				gameid 	= output[2]
				message	= output[3]
				emb 	= output[4]
				chans 	= output[5]
				for each in chans:
					mess = await each.send(embed=emb)
					msg["serverdata"]["games"][gameid]["publishid"].append((str(mess.id), str(mess.channel.id)))
				try:
					await output[0].send(message)
				except Forbidden:
					logger.warning(('\t' * tabs) + "Can't send to " + output[0].name + " as they have blocked me")
			elif output[1] == "List of outputups":
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Sending multiple messages from list of outputtups")
				if len(output) == 3 and type(output[2]) == type([]):
					for each in output[2]:
						try:
							await each[0].send(each[1])
						except Forbidden:
							logger.warning(('\t' * tabs) + "Can't send to " + each[0].name + " as they have blocked me")	
				else:
					logger.warning(('\t' * tabs) + "Somehow got wrong number of arguments or not a list for " + str(output))
				logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of multiple sends")		
			elif output[1] != "":
				if len(output[1]) > 2000:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Printing a string over 2000 chars")
					if "\n" in  output[1]: # chunk it into split lines
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Splitting into lines")
						result =  output[1].split("\n")
						msg = ""
						while len(result):
							if (len(msg) + len(result[0]) > 2000):
								try:
									await output[0].send(msg)
								except Forbidden:
									logger.warning(('\t' * tabs) + "Can't send to " + output[0].name + " as they have blocked me")	
								msg = ""						
							msg += result.pop(0) + "\n"
							if (len(result) == 0):
								try:
									await output[0].send(msg)
								except Forbidden:
									logger.warning(('\t' * tabs) + "Can't send to " + output[0].name + " as they have blocked me")	
					else: # chunk it into 2000 character chunks
						logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Splitting into 2000 character chunks")
						chunks, chunk_size = len(result), 2000
						messages = [ result[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
						for each in range(len(messages)):
							try:
								await output[0].send(messages[each])
							except Forbidden:
								logger.warning(('\t' * tabs) + "Can't send to " + output[0].name + " as they have blocked me")							
				else:
					logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Simple text output")
					try:
						await output[0].send(output[1])
					except Forbidden:
						logger.warning(('\t' * tabs) + "Can't send to " + output[0].name + " as they have blocked me")	
		except (Exception, DiscordException) as e:
			edata = PrintException()
			print("There was a problem sending an outputtup:\n" + str(edata))
			me = await ctx.bot.fetch_user(AUTHORID)
			await me.send(me.mention + " line " + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " There was a problem sending an outputtup:\n" + str(edata))		
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of roster")
	
bot.run(TOKEN)
