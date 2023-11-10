README for RosterRPG Bot
by TehManticore 2020

RosterRPG is a Discord bot for scheduling RPG game events with members of your Discord Server. It features:
- Creating and Editing events (Games)
- Players can list, roster, or sideline themselves for games
- Game times are given in the timezone specified by the player
- Players have an incrementing Priority number for every game they play in. 
- Listing for games automatically prioritises players with lower Priority number, switching out players with higher Priority number
- Players can see all upcoming games
- Server Owner can set levels of access for admins and GMs by Discord roles

~~~~~~~~~~ Quick Start Guide for Players ~~~~~~~~~~
1. Change your discord nickname to show your character level as the last 2 digits:
	For example, if @TehManticore has a character that's level 5, he will change his nickname to 
		@TehManticore 5 or 
		@TehManticore5 or 
		@TehManticore05
2. Check the timezones used by RosterRPG Bot:
	!roster timezones
3. Check what games are coming up:
	!roster games <your timezone>
4. Using the game id, get more information about the game:
	!roster <game id>
5. Submit yourself for listing with the game:
	!roster <gameid> roster me
6. Check your player priority:
	!roster priority
	
~~~~~~~~~~ Quick Start Guide for Game Masters ~~~~~~~~~~
1. Check the timezones used by RosterRPG Bot:
	!roster timezones
2. Create a new game:
	!roster newgame <timezone> <year> <month> <day> <24h:00>
	e.g. !roster newgame America/Phoenix 2020 04 25 23:10
3. Using the game id given from step 2, update the variables:
	!roster <game id> <variable> <new variable>
4. Review how your game info looks:
	!roster <game id>
5. Once you are satisfied, publish your game:
	!roster <game id> publish true
6. When the game has been played, mark your game as complete:
	!roster <game id> completed true


~~~~~~~~~~ Quick Start Guide for Server Owners ~~~~~~~~~~
1. Set your Game Masters:
	!roster settings roles 2 <mentioned discord roles>
2. Set the default settings that every new game will be created with (See the Game Variables above):
	!roster default <variable>						to see the current setting
	!roster default <variable> <new variable> 		to change the setting
3. Ask your players to show their character level at the end of their server nickname:
	The character level should be the last 2 digits of the nickname.
	For example, if @TehManticore has a character that's level 5, he will change his nickname to 
		@TehManticore 5 or 
		@TehManticore5 or 
		@TehManticore05
4. Set a text channel to have all future games published to:
	!roster settings gamelistingchannel <mentioned discord text channel>


----------------------------------------------------------		
Commands for PLAYERS
(authority level 3)
----------------------------------------------------------		
!roster							Info about the bot
!roster timezones				Whispers the usable timezones to the player
!roster games					Lists all future games that have been published
!roster games <timezone> 		Lists upcoming game with the given timezone
!roster games unpublished		Lists all games, whether published or not
!roster priority				Tells you what your player Priority level is (from 1 to n)
!roster <gameid> roster me		Attempts to add you to the roster of the given game based on your Priority level
!roster <gameid> sideline me	As above but for sidelines only



----------------------------------------------------------		
Commands for GAME MASTERS 
(authority level 2)
----------------------------------------------------------		
!roster newgame <timezone> <date and time> 		Creates a new game event at the given date and time. date and time is given from largest to smallest, in 24h clock.
												Example: !roster newgame America/Phoenix 2020 04 25 23:10
												Gives you the Game ID needed for editing and publishing the game event to Discord

!roster <gameid> 								Prints out the publishable game info
!roster <gameid> <variable>						Reports the given variable of the given game (using gameid)
!roster <gameid> <variable> <new variable>		Changes the variable to the new variable given

Game Variables are:
	Server								Discord Server ID. Can't be changed.
	id									Unique Game Event ID. Can't be changed.
	gm									Server member that is the Game Master for this event. Automatically assigned to the member that created the event.
	name								Custom name given to the event. 50 characters max.
	session								Custom numeric identifier to signify a number for the event (such as session number, or progress through current campaign). E.g. "4" or "6.1"
	description							Custom description for this event. 200 characters max.
	timezone							Timezone that was given when the game was created.
	datetime							Date and time for the game. Players that request this time will have it converted to the timezone they give.
	minplayers							Number for how many players are needed for this event.
	maxplayers							Number for the upper limit of players for this event.
	sidelineson							Whether players can go on the sidelines to fill vacant spots that come up
	minsidelines						Number for a required number of sidelined players ("backups"). Defaults to 0
	maxsidelines						Number for the upper limit of players that can be sidelined for this event. Defaults to maxplayers
	textchannel							Name of the Discord Text Channel that will be used for this event. Requires the channel to be mentioned using #
	voicechannel						Name of the Discord Text Channel that will be used for this event. Doesn't require channel mention using #, but does need to match the voice channel by name
	roster								The list of players for this event. 
	roster <mentioned player> 			Used to add or remove that player from this list. 
										Players are added based on their Priority level, and may not get added if there are no free spots or all rostered players have better priority.
	roster <mentioned player> fixed		Used to add the player in a "fixed" state that won't be bumped based on priority.
	sideline							The list of players for this event. 
	sideline <mentioned player>			Used to add or remove that player from this list.
	gpreward							Custom entry for Gold Piece Reward for the game. 20 characters max.
	xpreward							Custom entry for Experience Point Reward for the game. 20 characters max.
	duration							Custom entry for estimated duration of the event. 20 characters max
	minlevel							Number for the lowest level characters accepted to this game. Must be a number. Is limited by Server setting playerminlevel
	maxlevel							As above but highest level, limited by Server playermaxlevel
	tier								Number or word to represent categories of players
	completed							Whether the game has finished. Marking a game completed will increment each rostered player's Priority Level for that game. Accepts true and false
	publish								Whether the game is published to the text channel assigned in Server setting gameannouncementschannel. Accepts true and false.


----------------------------------------------------------			
Commands for SERVER OWNER and ADMINISTRATORS 
(authority level 1)
----------------------------------------------------------		
!roster settings												Prints all current Server Settings
!roster settings <variable | subvariable>						Prints the current Server Setting for the given variable and subvariable
!roster settings <variable | subvariable > <new variable>		Changes the current setting for the new variable given.
																If the variable is stored in list form, then the list will either add or remove the given new variable.

Server Settings are:

authority						Stores authority levels can use which Roster Bot functions
									Use !roster settings authority <sub variable> to get the current setting
									Use !roster settings authority <sub variable> <new variable> to change the setting
								Each takes a number from 1-4. The number shown is the default setting.
								
	authority settings			1 Who can view and change roster bot settings
	authority default			1 Who can view and change the default data given to all new games
	authority newgame			2 Who can create new games
	authority gameid			2 Who can view and change game data.
	authority list				2 Who can list any player for a given game. If the player can't be rostered due to Priority Level or not enough spaces, they will be added to sidelines.
	authority roster			2 Who can roster any player for a given game. If the player can't be rostered, they won't be added to sidelines.
	authority sideline			2 Who can sidelines any player for a given game. If the player can't be sidelined due to not enough spaces, they won't be added to the game.
	authority priority			3 Who can view any player priority levels
	authority timezones			3 Who can get the timezones
	authority games				3 Who can see upcoming games
	authority game				3 Who can view game data
	authority listme			3 Who can list themselves for a given game
	authority rosterme			3 Who can roster themselves for a given game (won't add to sidelines)
	authority sidelineme		3 Who can sideline themselves for a given game (won't add to roster)	
	
roles							Each role numbered lists which Discord Roles are assigned to each authority level
									Use !roster settings role <number> to see the current list of discord roles.
									Use !roster settings role <number> <discord role> to add or remove the given Discord Role to the list
								
	roles 1						Roles with "Administrator" status who has the ighest authority level for the bot and can use all commands. Server Owner always has authority level 1.				
	roles 2						Roles with "Game Master" status who can use Authority Level 2 bot commands and below. If this list is empty, then it includes @everyone
	roles 3						Roles with "Player" status and can use only Authority Level 3 bot commands. If this list is empty, then it includes @everyone
	roles 4						Roles with "Forbidden" status. Members in this role (other than Server Owner) are excluded from all use of Roster Bot.

gamelistingchannel				Lists what text channels new games are published to when the maker sets publish to true
									Use !roster settings gamelistingchannel <discord text channel> to add or remove a channel


playerminlevel					Stores the lowest player level that a game can have minlevel set to
								Must be a number
playermaxlevel					Stores the highest player level that a game can have maxlevel set to
								Must be a number

playermaxroster					Stores how many incomplete (future) games a single player can be rostered for at a time. 
								Defaults to -1 which means no limit.
playermaxconsecutive			Stores how many games a player can play immediately after finishing a game (consecutive games in a row). 
								Defaults to -1 which means no limit. 
								0 means players can't be rostered for consecutive games.
								1 means players can be rostered for only one game after a first, etc.
								
								



	
