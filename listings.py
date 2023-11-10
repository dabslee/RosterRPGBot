from config import *

async def ListPlayer(ctx, ServData, SS, memberobj, gamedict, priv, listing="both", fixed="unfixed", whisper=False):
	""" Adds a player to either the Roster or Sidelines for a game """
	logger.debug(tb(tabs) + "Start of ListPlayer")
	logger.debug(("\t" * (tabs+1)) + "Data received:")
	for each in [("ctx", ctx), ("member", memberobj), ("gameid", gamedict["id"]), ("priv", priv), ("listing", listing), ("fixed", fixed)]:
		logger.debug(("\t" * (tabs+1)) + each[0] + ": " + str(each[1]))

	gameid  = gamedict["id"]
	pid		= str(memberobj.id)
	outputlist = []
	chan = ctx
	if whisper and not memberobj.bot:
		chan = memberobj
	
	logger.debug(("\t" * (tabs+1)) + "Checking how many times to loop through this function")	
	sendtosideline = False # whether to call ListPlayer>sideline after this
	other = "sideline"
	if listing == "both":
		logger.debug(tb(tabs+2) + "Looping for Roster AND Sideline")
		sendtosideline = True
		listing = "roster"
	elif listing == "sideline":
		logger.debug(tb(tabs+2) + "Just going through sideline")
		other = "roster"
	else:
		logger.debug(tb(tabs+2) + "Just going through roster")
	logger.debug(("\t" * (tabs+1)) + "listing: " + listing + ", other: " + other)
	logger.debug(("\t" * (tabs+1)) + "current player " + listing + ": " + str(gamedict[listing]))
				 
	# Step 0 - Check if Sidelines is on
	logger.debug(("\t" * (tabs+1)) + "Step 0 - Check if Sidelines is on")
	if listing == "sideline" and gamedict["sidelineson"] == "0":
		logger.debug(tb(tabs+2) + "Sidelines isn't on")
		return (ctx, memberobj.mention + " There are no sidelines allowed for game " + gameid)
	logger.debug(("\t" * (tabs+1)) + "Step 0 Passed")

	logger.debug(("\t" * (tabs+1)) + "Step 0.5 - Get the authority to use fixed status")
	fixedauth = False
	authname = "rosterfixed"
	if listing == "sideline":
		authname = "sidelinefixed"
	logger.debug(tb(tabs+2) + "authname: " + str(authname))
	fixedauth = AuthorityCheck(SS, ctx.message.author, authname, priv, "settings", subc="authority", gamedict=gamedict)[0]
	logger.debug(tb(tabs+2) + "fixedauth: " + str(fixedauth))
	
	# Step 1 - Check if player is in current list
	logger.debug(("\t" * (tabs+1)) + "Step 1 - Check if player is in current list")
	pids = [pl[0] for pl in gamedict[listing]]
	if pid in pids:
		logger.debug(tb(tabs+2) + "Player is in " + listing + " list")
		pos = pids.index(pid)
		logger.debug(tb(tabs+2) + "Pos: " + str(pos))
		status = gamedict[listing][pos][1]
		logger.debug(tb(tabs+2) + "Status: " + status)

		# Step 1.1 - Check if player is changing their fixed/unfixed status
		logger.debug(("\t" * (tabs+1)) + "Step 1.1 - Check if player is changing their fixed/unfixed status")
		if status != fixed:
			logger.debug(tb(tabs+2) + "Updating status")
			if fixed == "fixed":
				logger.debug(tb(tabs+2) + "Checking if message author has permission to change status to fixed")
				logger.debug(tb(tabs+2) + "listing: " + str(listing))
				if fixedauth == False:
					logger.debug(tb(tabs+2) + "Authority not allowed")
					return (ctx, memberobj.mention + " You do not have authority to change status to fixed")
				gamedict[listing][pos] = (pid, fixed)
				await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
				return (ctx, "The " + listing + " status for player " + memberobj.mention + " in game " + gameid + " has been changed from " + status + " to " + fixed)
			else:
				logger.debug(tb(tabs+2) + "Not updating status. Already in list")
				return (ctx, memberobj.mention + " is already in the " + listing + " for game " + gameid + " (" + status + ")" )
	logger.debug(("\t" * (tabs+1)) + "Step 1 Passed")
	
	# Step 2 - Check if player is in other listing and fixed
	logger.debug(("\t" * (tabs+1)) + "Step 2 - Check if player is in other listing and fixed")
	otherlistpos = None
	pids = [pl[0] for pl in gamedict[other]]
	if pid in pids:
		logger.debug(tb(tabs+2) + "Player is in " + other + " list")
		otherlistpos = pids.index(pid)
		logger.debug(tb(tabs+2) + "Pos: " + str(otherlistpos))
		status = gamedict[other][otherlistpos][1]
		logger.debug(tb(tabs+2) + "Status: " + status)

		# Step 2.1 - Check if player is fixed in other
		logger.debug(("\t" * (tabs+1)) + "Step 2.1 - Check if player is fixed in other status")
		if status == "fixed" and fixed == "unfixed" and fixedauth == False:
			logger.debug(tb(tabs+2) + "Player is fixed")
			return (ctx, memberobj.mention + " is listed as \"fixed\" for the " + other + " in game " + gameid + ". Can't add to " + listing + " until they are manually removed from the " + other)		
		logger.debug(tb(tabs+2) + "Member is not fixed")
	logger.debug(("\t" * (tabs+1)) + "Step 2 Passed")
	
	# Step 3 - Check that player is of matching level
	logger.debug(("\t" * (tabs+1)) + "Step 3 - Check that player is of matching level")	
	logger.debug(("\t" * (tabs+1)) + "Getting player's level from their nickname")
	member = ctx.guild.get_member(memberobj.id)
	theirnick = member.nick
	if theirnick == None:
		theirnick = member.display_name
	logger.debug(("\t" * (tabs+1)) + "theirnick: " + theirnick)	
	level = GetCharLevel(theirnick, tabs=tabs)
	if type(level) == type(""):
		logger.debug(tb(tabs+2) + level)
		return (ctx, memberobj.mention + " " + level)
	
	if level < 	int(gamedict["minlevel"]):
		logger.debug(tb(tabs+2) + "Character level " + str(level) + " is below minlevel " + str(gamedict["minlevel"]))
		return (ctx, memberobj.mention + " Character level " + str(level) + " is below minlevel " + str(gamedict["minlevel"]))		

	if level > 	int(gamedict["maxlevel"]):
		logger.debug(tb(tabs+2) + "Character level " + str(level) + " is below maxlevel " + str(gamedict["maxlevel"]))
		return (ctx, memberobj.mention + " Character level " + str(level) + " is above maxlevel " + str(gamedict["maxlevel"]))
	logger.debug(("\t" * (tabs+1)) + "Step 3 Passed")

	# Step 4 - Check that player isn't listed in too many games
	logger.debug(("\t" * (tabs+1)) + "Step 4 - Check that player isn't listed in too many games")
	logger.debug(tb(tabs+2) + "Getting list of future games")
	future = ServData["players"][str(memberobj.id)]['r']
	maxallowed = SS["settings"]["playermaxroster"]
	plural2 = "rostered" # for the output message below
	verb = "rostering"
	if listing == "sideline":
		maxallowed = SS["settings"]["playermaxsideline"]
		future = ServData["players"][str(memberobj.id)]['s']
		plural2 = "sidelined"
		verb = "sidelining"
	logger.debug(tb(tabs+2) + "Max allowed: " + maxallowed + ". Future games: " + str(future))
	
	logger.debug(tb(tabs+2) + "Player is in the " + listing + "for "  + str(len(future)) + " future games")
	if len(future) and int(maxallowed) >= 0:
		logger.debug(tb(tabs+2) + "Checking limit")
		if len(future) >= int(maxallowed):
			logger.debug(tb(tabs+2) + "Has too many future rostered games")
			plural = str(len(future)) + " game"			
			if len(future) > 1:
				plural += "s"
			return (ctx, memberobj.mention + " is already " + plural2 + "  for " + plural + "\nPlease unlist down to " + str(int(maxallowed)-1) + " game/s before " + verb + " for more")
		logger.debug(tb(tabs+2) + "Player is within limits")
		
		# Step 4.1: Check that player isn't playing more games in a row than playermaxconsecutive
		logger.debug(("\t" * (tabs+1)) + "Step 4.1 - Check that player isn't listed in too many games")
		consec = SS["settings"]["playermaxconsecutive"]
		logger.debug(tb(tabs+2) + "Consecutive games is: " + consec)
		if int(consec) >= 0 and listing == "roster":
			logger.debug(tb(tabs+2) + "Checking consecutive games")
			conseccount = CheckConsecutiveRosters(ServData, str(member.id), gameid)
			logger.debug(tb(tabs+2) + "Has " + str(consec) + " games rostered")
			if conseccount > int(consec):
				logger.debug(tb(tabs+2) + "Player has too many consecutive games lined up. Limit: " + consec)
				return (ctx, memberobj.mention + " can't be listed for game " + gameid + " because the player will have played too many games in a row")		
	logger.debug(("\t" * (tabs+1)) + "Step 4 Passed")
	
	# Step 5 - Check if there are empty spaces
	logger.debug(("\t" * (tabs+1)) + "Step 5 - Check if there are empty spaces")
	maxp = int(gamedict["maxplayers"])
	if listing == "sideline":
		maxp =  int(gamedict["maxsidelines"])
	listed = len(gamedict[listing])
	logger.debug(tb(tabs+2) + "Listed: " + str(listed) + ". Max Players: " + str(maxp))
	newpos = "end"
	if listed >= maxp:
		logger.debug(tb(tabs+2) + "There were no free spots")	
		
		# Step 5.1: Check if there is a lower priority listed player
		logger.debug(("\t" * (tabs+1)) + "Step 5.1 - Check if there is a lower priority player")
		thisp = CalcPlayerPriority(ServData, str(member.id))
		logger.debug(tb(tabs+2) + "This player's priority: " + str(thisp))
		higherp = []
		for pos, (pl, status) in enumerate(gamedict[listing]):
			pdata = (pos, pl, CalcPlayerPriority(ServData, pl))
			if pdata[2] > thisp and status != "fixed":
				higherp.append(pdata)
		logger.debug(tb(tabs+2) + "Worse priority players: " + str(higherp))
		
		if len(higherp) == 0:
			logger.debug(tb(tabs+2) + "No worse priority players and no room")
			output = (chan, memberobj.mention + " unable to " + listing + " for game " + gameid + " because there are no unfixed players of lower priority")
			outputlist.append(output)
			if sendtosideline:
				logger.debug(tb(tabs+2) + "Sending this player to sidelines")
				output = await ListPlayer(ctx, ServData, SS, memberobj, gamedict, priv, listing="sideline", fixed=fixed, whisper=whisper)
				if type(output) == type([]):
					outputlist += output
				else:
					outputlist.append(output)
			elif otherlistpos != None:
				# Step 5.11 - removing from other list, if necessary
				logger.debug(("\t" * (tabs+1)) + "Step 5.11 - removing from other list, if necessary")
				logger.debug(("\t" * (tabs+1)) + "Removing from other: " + other + " at pos " + str(otherlistpos))
				if gamedict[other][otherlistpos][0] == pid:
					del gamedict[other][otherlistpos]
					RemoveFromTeam(ServData, gameid, pid, other, removefixed=fixed)
					output = (chan, memberobj.mention + " was removed from " + listing + " to make the switch")
					outputlist.append(output)
				logger.debug(("\t" * (tabs+1)) + "Other " + other + " list is now: " + str(gamedict[other]))	
				logger.debug(("\t" * (tabs+1)) + "Step 5.11 Complete")
			else:
				logger.debug(tb(tabs+2) + "Not sending to sidelines")
			logger.debug(tb(tabs+2) + "Outputlist: " + str(outputlist))
			return outputlist

		# Step 5.2 - Sideline or remove lower priority player
		logger.debug(("\t" * (tabs+1)) + "Step 5.2 - Sideline or remove lower priority player")
		
		logger.debug(tb(tabs+2) + "Lower priority player found. Getting their position")	
		higherp = sorted(higherp, key=lambda element: (element[2], element[0]))
		logger.debug(tb(tabs) + "List of players sorted by priority then position: " + str(higherp))
		newpos = higherp[-1][0]
		upid = higherp[-1][1]
		logger.debug(tb(tabs) + "Player with worse priority is at roster position " + str(newpos) + ", id " + str(upid))
		if listing == "roster":
			logger.debug(tb(tabs+2) + "Sidelining worse priority player " + str(upid))
			otherpobj = ctx.bot.get_user(int(upid))
			logger.debug(tb(tabs+2) + "Other player object: " + str(otherpobj))
			output = await ListPlayer(ctx, ServData, SS, otherpobj, gamedict, priv, listing="sideline", whisper=True) # this will also take the player out of the other list
			if type(output) == type([]):
				outputlist = outputlist + output
			else:
				outputlist.append(output)
		else:
			logger.debug(tb(tabs+2) + "Removing player from sideline as it has reached it's maximum")
			del gamedict[listing][newpos]
			othermember = ctx.bot.get_user(int(upid))
			if othermember != None:
				output = (othermember, othermember.mention + "You have been removed from the sidelines for game " + gameid + " as there are too many listed")
				outputlist.append(output)
	logger.debug(("\t" * (tabs+1)) + "Step 5 Passed")
	
	# Step 6 - Add the player at the stored position
	logger.debug(("\t" * (tabs+1)) + "Step 6 - Add the player at the stored position")
	
	logger.debug(tb(tabs+2) + "Checking if user has authority to use fixed status")
	if fixed == "fixed":
		logger.debug(tb(tabs+2) + "Requesting fixed status")
		authname = "rosterfixed"
		if listing == "sideline":
			authname = "sidelinefixed"
		auth = SS["settings"]["authority"][authname]
		logger.debug(tb(tabs+2) + "Authority level is " + auth + " and priv is " + str(priv))
		if priv > int(auth):
			logger.debug(tb(tabs+2) + "Authority not allowed. Using unfixed")
			output = (chan, memberobj.mention + " You do not have authority to change status to fixed. Using unfixed")
			fixed = "unfixed"
	logger.debug(tb(tabs+2) + "Authority for status passed")
		
	if newpos == "end":
		logger.debug(tb(tabs+2) + "Adding the player straight to the end")
		gamedict[listing].append((pid, fixed))
	else:
		logger.debug(tb(tabs+2) + "Inserting player at position " + str(newpos))
		gamedict[listing].insert(newpos, (pid, fixed))
	output = (chan, memberobj.mention + " has been added to the " + listing + " for game " + gameid)
	outputlist.append(output)
	logger.debug(("\t" * (tabs+1)) + "Step 6 Passed")
	logger.debug(tb(tabs) + listing + " is now: " + str(gamedict[listing]))
	logger.debug(("\t" * (tabs+1)) + "Output so far: ")
	for each in outputlist:
		logger.debug(tb(tabs+2) + str(each))

	# Step 7 - Updating the player's recorded listings
	logger.debug(("\t" * (tabs+1)) + "Step 7 - Updating the player's recorded listings")
	letter = 'r'
	if listing == "sideline":
		letter = 's'
	logger.debug(("\t" * (tabs+1)) + "Player's \"" + letter + "\" list was: " + str(ServData["players"][pid][letter]))
	if gameid not in ServData["players"][pid][letter]:
		logger.debug(("\t" * (tabs+1)) + "Adding " + gameid + " to letter " + letter)
		ServData["players"][pid][letter].append(gameid)
	logger.debug(("\t" * (tabs+1)) + "Player's \"" + letter + "\" list is now: " + str(ServData["players"][pid][letter]))
	logger.debug(("\t" * (tabs+1)) + "Step 7 Complete")
	
	# Step 8 - removing from other list, if necessary
	logger.debug(("\t" * (tabs+1)) + "Step 8 - removing from other list, if necessary")
	if otherlistpos != None:
		logger.debug(("\t" * (tabs+1)) + "Removing from other: " + other + " at pos " + str(otherlistpos))
		if gamedict[other][otherlistpos][0] == pid:
			del gamedict[other][otherlistpos]
			output = (chan, memberobj.mention + " was removed from " + other + " to make the switch")
			outputlist.append(output)
			logger.debug(("\t" * (tabs+1)) + "Updating player's roster/sideline record")
			RemoveFromTeam(ServData, gameid, pid, team=other, removefixed=True)
	logger.debug(("\t" * (tabs+1)) + "Other " + other + " list is now: " + str(gamedict[other]))	
	logger.debug(("\t" * (tabs+1)) + "Output so far: ")
	for each in outputlist:
		logger.debug(tb(tabs+2) + str(each))
	logger.debug(("\t" * (tabs+1)) + "Step 8 Complete")
	
	# Step 9 - Sending Updates
	author = None
	aid	   = None
	if type(ctx) == type(ext.commands.Context):
		author = ctx.message.author
		aid    = author.id
	logger.debug(("\t" * (tabs+1)) + "author: " + str(author))
	
	logger.debug(("\t" * (tabs+1)) + "Step 9 - Sending Updates")
	logger.debug(tb(tabs+2) + "Prepping a message for the author for each message created so far that wasn't for them")
	ocopy = outputlist[:]
	logger.debug(tb(tabs+2) + "ocopy: " + str(ocopy))
	logger.debug(tb(tabs+2) + "ctx.message.author: " + str(author))
	for each in ocopy:
		logger.debug(tb(tabs+3) + "This message: " + str(each))
		if each[0] == author or each[0] == ctx: # Don't repeat output to ctx from above, such as for ListMe
			logger.debug('\t\t\t\t\t' + "Not adding: same recipient")
		else:
			logger.debug('\t\t\t\t\t' + "New message. Adding")
			outputlist.append((ctx, each[1]))			
	logger.debug(("\t" * (tabs+1)) + "Output before adding others that should be alerted: " + str(outputlist))
	msg = {"serverdata": ServData, "ctx": ctx, "guild": ctx.guild, 	"ss": ServData, "ac": Commands.AC, "author":ctx.author,"uargs":[],"numargs":0,"authority":priv}
	users = CollateUpdateMsgs(msg, gameid, group=listing)
	logger.debug(("\t" * (tabs+1)) + "Users: " + str([u.name for u in users]))
	for player in users:
		logger.debug(tb(tabs+2) + "Checking " + str(player.name) + ", obj: " + str(player))
		if player.id != aid and player.id != memberobj.id and player.bot == False:	# Don't notify the person that got 		
			logger.debug(tb(tabs+2) + "Sending to them")
			ocopy = outputlist[:]
			logger.debug(tb(tabs+2) + "ocopy: " + str(ocopy))
			for each in ocopy:
				logger.debug(tb(tabs+3) + "This message: " + str(each))
				if each[0] == player: # Don't repeat output to ctx
					logger.debug('\t\t\t\t\t' + "Message will already be sent to this person. Not adding")
				else:
					logger.debug('\t\t\t\t\t' + "Person hasn't received this message so far. Adding")
					outputlist.append((player, each[1]))					
		else:
			logger.debug(tb(tabs+2) + "Skipping as is the message sender, the whispered member, or a bot")
	logger.debug(("\t" * (tabs+1)) + "Finished Sending Updates")
	logger.debug(("\t" * (tabs+1)) + "Output at the end: ")
	for each in outputlist:
		logger.debug(tb(tabs+2) + str(each))	

	await UpdateGameEmbeds(msg, gameid, "update", tabs=tabs)
	
	logger.debug(tb(tabs) + "End of ListPlayer")
	return outputlist

class ListMod():
	
	
	def __init__(self, ctx, ServData, authorobj, playerobj, gameid, priv, listing="both", fixed="unfixed", output=[], tabs=0):
		logger.debug(tb(tabs) + "Creating ListMod")
		tabs += 1
		logger.debug(tb(tabs) + "ListMod Data: ")
		logger.debug(tb(tabs) + "ServData: " + str(ServData.items()))
		logger.debug(tb(tabs) + "authorobj: " + str(authorobj.items()))
		logger.debug(tb(tabs) + "playerobj: " + str(playerobj.items()))
		logger.debug(tb(tabs) + "gameid: " + str(gameid))
		logger.debug(tb(tabs) + "priv: " + str(priv))
		logger.debug(tb(tabs) + "listing: " + str(listing))
		logger.debug(tb(tabs) + "fixed: " + str(fixed))
		logger.debug(tb(tabs) + "output: " + str(output))
		
		self.ctx 		= ctx
		self.ServData 	= ServData
		self.authorobj 	= authorobj
		self.aid		= str(authorobj.id)
		self.playerobj 	= playerobj
		self.pid		= str(playerobj.id)
		self.gameid		= gameid
		self.gamedict   = ServData["games"][gameid]
		self.priv		= priv
		self.listing	= listing
		self.fixed		= fixed
		self.output		= output
		
		logger.debug(tb(tabs) + "End of Creating ListMod")

		
	def Start(self, tabs=0):
		logger.debug(tb(tabs) + "Start of ListMod.Start")
		tabs += 1		

	def CheckListOrcer(self, tabs=0):	
		logger.debug(("\t" * (tabs+1)) + "Checking how many times to loop through this function")	
		sendtosideline = False # whether to call ListPlayer>sideline after this
		other = "sideline"
		if listing == "both":
			logger.debug(tb(tabs+2) + "Looping for Roster AND Sideline")
			sendtosideline = True
			listing = "roster"
		elif listing == "sideline":
			logger.debug(tb(tabs+2) + "Just going through sideline")
			other = "roster"
		else:
			logger.debug(tb(tabs+2) + "Just going through roster")
		logger.debug(("\t" * (tabs+1)) + "listing: " + listing + ", other: " + other)
		logger.debug(("\t" * (tabs+1)) + "current player " + listing + ": " + str(gamedict[listing]))