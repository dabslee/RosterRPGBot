import logging
import inspect
import time
import os
import sys
import traceback
import shutil
import linecache
import glob
import operator
from pytz import timezone
from datetime import datetime
from pathlib import Path
from disctoken import MAINTENANCE

AUTHORID = int("590439531199725578") #TehManticore's ID
BOT_PREFIX = ("!")
MYTZ = "Australia/Melbourne"

# Bot settings to prevent processing abuse and overuse
UPDATEFREQ = 60 # Number of seconds between checks and file updates of servers
FILEDUMPDELAY = 60 # Number of seconds between requests for filedumps
PLAYERRESPONSETIME = 5 # Number of seconds between player requests
FILEDUMPSIZE = 7.5 # MB before debug AND nohup.out are sent to be and cleared.
DELETECOMPLETEDGAMES = 31 # Number of days since a completed game was played before deleting it from records

# Other globals
MASTERROLE 		= ["Server Owner", "Bot Author"]
MALICIOUS 		= ["{", "}", "\"", "\\"] # characters that need to be cleaned from the given arguments
TFORMAT 		= "%Y %m %d %H:%M"
TFORMATDASH 	= "%Y %m %d %H-%M" # Used for logging
TFORMATDASHS	= TFORMATDASH+"-%S" # Used for logging
TDFORMAT 		= "%Y %m %d %a %H:%M"
TDFORMATSHORT   = "%y-%m-%d %a %H:%M"
DTERROR 		= "Time must be in large to small format: Timezone Year Month Day 24H:MM. For example: America/Phoenix 2020 04 25 23:10\n"
DTERROR		   += "Type !rb alltimezones to see the list of timezones you can use. Provide one in your command or use !rb mytimezone to set yours"
FIXSTR 			= ["unfixed", "fixed"] # uses false and true
TOGGLEON 		= ["1", "true", "on", "yes"]
TOGGLEOFF 		= ["0", "false", "off", "no"]
TOGGLEOFFON 	= ["Off", "On"]
TOGGLEFT 		= ["False", "True"]
TOGGLENY 		= ["No", "Yes"]

COLOURS = { "default": 0, "teal": 0x1abc9c, "dark_teal": 0x11806a, "green": 0x2ecc71, "dark_green": 0x1f8b4c, "blue": 0x3498db, "dark_blue": 0x206694, "purple": 0x9b59b6, "dark_purple": 0x71368a,
		   "magenta": 0xe91e63, "dark_magenta": 0xad1457, "gold": 0xf1c40f, "dark_gold": 0xc27c0e, "orange": 0xe67e22, "dark_orange": 0xa84300, "red": 0xe74c3c, "dark_red": 0x992d22, "lighter_grey": 0x95a5a6,
		   "dark_grey": 0x607d8b, "light_grey": 0x979c9f, "darker_grey": 0x546e7a, "blurple": 0x7289da, "greyple": 0x99aab5}

def tb(tabs):
	return "\t" * tabs

def PrintException():
	# From https://stackoverflow.com/questions/14519177/python-exception-handling-line-number/20264059 by yedpodtrzitko,  accessed 28/0920
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


#Set up logger

# Get the directory of this file
ParentDir = Path(__file__).parent

# Check if a Debug directory exists and make it if not
DebugFilepath = ParentDir.joinpath("debug")
#print("Debug output to " + str(DebugFilepath))
try:
	if not DebugFilepath.exists():
		Path.mkdir(DebugFilepath)
except:
	stack = traceback.extract_stack()
	e = traceback.format_exc(stack[1])
	print(str(e))

logformat = '%(asctime)s:%(levelname)s:\t %(message)s'
#logging.basicConfig(format=logformat, datefmt=TFORMATDASHS)
def loggingtime(*args): # From Ryan J McCall, https://stackoverflow.com/questions/32402502/how-to-change-the-time-zone-in-python-logging, accessed 14/09/2020
	try:
		utc = timezone("UTC")
		utc_dt = utc.localize(datetime.utcnow())
		converted = utc_dt.astimezone(timezone(MYTZ))
		return converted.timetuple()
	except Exception as e:
		edata = PrintException()
		print(edata)

class MyTzFormatter(logging.Formatter):
	converter = loggingtime

logger = logging.getLogger('rosterbot')
logger.setLevel(logging.DEBUG)
logger.propagate = False

def GenerateLogFile():
	""" Used each time a log file is created """
	return DebugFilepath / ("rosterbot debug " + datetime.now(timezone(MYTZ)).strftime(TFORMATDASHS) + ".log")

logfilepath = GenerateLogFile()

def ResetHandler(thislogger, flpath):
	handler = logging.FileHandler(filename=flpath, encoding='utf-8')
	handler.setFormatter(MyTzFormatter(fmt=logformat, datefmt=TFORMATDASHS))
	for hdlr in thislogger.handlers[:]:  # remove all old handlers
		thislogger.removeHandler(hdlr)
	thislogger.addHandler(handler)
	
ResetHandler(logger, logfilepath)
logger.warning("Program started")


#~~~~~~~~~~~~~~~~~ UPTIME LOGGING ~~~~~~~~~~~~~~~~~~~~~~~~~~
uptimetxt = Path(__file__).parent / "uptime.log"
concount = 0	# stores how many times the program has connected
utcreate = " Uptime.log was created\n"
utclose = " Bot was successfully shutdown\n"
utfail = "Bot Program was not shutdown properly\n"
utstart = " Bot Program was started\n"
utcon	= " Bot connection to Discord count: "
utresume = " Bot resumed connection to Discord\n"
utdiscon = " Bot DISconnected from Discord\n"
NOW = datetime.now(timezone(MYTZ)).strftime(TFORMATDASHS)
BADSTART = False
LASTRUN = None # time of last uptime message

try:
	if not uptimetxt.exists():
		with open(uptimetxt, 'a') as f:
			f.write( NOW + utcreate)
except Exception as e:
	edata = PrintException()
	print(edata)

def updateNOW():
	NOW = datetime.now(timezone(MYTZ)).strftime(TFORMATDASHS)
	return NOW
		
def uptimestart():
	""" Records the start time of the Bot Program """
	with open(uptimetxt, 'a') as f:	
		f.write(updateNOW() + utstart)

def uptimechk():
	""" Checks if the Bot shutdown ok and adds a message if not
	Returns True False so it can send me the result in a message in discord """
	global BADSTART, LASTRUN
	with open(uptimetxt, 'r') as f:
		lines = f.read().splitlines()
		if len(lines) > 1: # file wasn't just created
			last_line = lines[-1]
			oks = [utclose, utcreate, utdiscon]
			for each in oks:
				if each[:-1] not in last_line:
					BADSTART = True
					LASTRUN = last_line[:16] # get the date time
					break
	if BADSTART == True:
		with open(uptimetxt, 'a') as f:	
			f.write(utfail)
			print(updateNOW() + " " + utfail + "Last uptime message: " + LASTRUN)
			
def uptimecon():
	""" Records when the Bot connected to discord and how many times now """
	global concount
	with open(uptimetxt, 'a') as f:
		f.write(updateNOW() + utcon + str(concount) + '\n')
	concount += 1

def uptimeresume():
	""" Records when the Bot Resumed connection to discord """
	with open(uptimetxt, 'a') as f:
		f.write(updateNOW() + utresume)
		
def uptimediscon():
	""" Records when the Bot DISconnected to discord """
	with open(uptimetxt, 'a') as f:
		f.write(updateNOW() + utdiscon)
		
def uptimeclose():
	""" Records proper shutdown of the Bot Program (using !rb quit, etc) """
	with open(uptimetxt, 'a') as f:
		f.write(updateNOW() + utclose)	

# run when program is run
#uptimechk()	   # check last shutdown
uptimestart()  # add current start time

# Function from https://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python seen 13/04/20
class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

def PrintAttrMeth(thing): # For printing out the methods and variables of objects?
	for item in vars(thing).items():
		print(str(item))
	object_methods = [method_name for method_name in dir(thing) if callable(getattr(thing, method_name))]
	for item in object_methods:
		print(str(item))

def IsInt(text, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of IsInt with " + str(text))
	tabs += 1
	try:
		int(text) # convert to int
	except ValueError:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(text))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of IsInt")
		return False

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of IsInt")
	return True

def IsFloat(text, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of IsFloat with " + str(text))
	tabs += 1
	try:
		float(text) # convert to int
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " It's a float")
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of IsFloat")
		return True
	except ValueError:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(text))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of IsFloat")
		return False	

def IsNumber(text, tabs=0): # Copied from https://stackoverflow.com/questions/34425583/how-to-check-if-string-is-int-or-float-in-python-2-7/37138024, rajesh.kanakabandi, accessed 17/09/20
    ''' return 1 for int, 2 for float, 0 for not a number'''
    try:
        float(text)
        return 1 if text.count('.')==0 else 2
    except ValueError:
        return 0

def StrToInt(text, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of StrToInt with " + str(text))
	tabs += 1
	num = ""
	try:
		num = int(text) # convert to int
	except ValueError:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Couldn't convert the given value to an int: " + str(text))
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StrToInt")
		return ""

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StrToInt")
	return num

def StrToNumber(text, tabs=0):
	""" """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of StrToNumber with " + str(text))
	tabs += 1
	num = ""
	try:
		float(text)
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StrToNumber")
		return int(text) if text.count('.')==0 else float(text)
	except ValueError:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of StrToNumber")
		return ""

def StrOrUnset(text, tabs=0):
	""" Checks if a str has characters and if not, returns "Unset" """
	if len(text):
		return text
	return "unset"

def deeplogdict(data, level="debug", tabs=0):
	""" Prints data to the logger """
	#logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of deeplogdict")
	tabs += 1
	levels = {"debug": logger.debug, "warning": logger.warning, "warn":logger.warning, "info": logger.info}
	tabstr = '\t' * tabs
	if isinstance(data, str):
		func = levels[level]
		func(tabstr + str(data))	
	elif isinstance(data,tuple):
		func = levels[level]
		func(tabstr + str(data))
	elif isinstance(data,list):
		levels[level](tabstr + "[")
		for item in data:
			deeplogdict(item, level, tabs+1)
		levels[level](tabstr + "]")
	elif isinstance(data,dict) or isinstance(data,AutoVivification):
		levels[level](tabstr + "{")
		for key, item in data.items():
			levels[level](tabstr + str(key) + ": ")
			deeplogdict(item, level, tabs+1)
		levels[level](tabstr + "}")
	else:
		func = levels[level]
		func(tabstr + str(data))	
	
	if tabs <= 1:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of deeplogdict")

def deeplogdictstr(data, output="", tabs=0):
	""" Outputting to a string for print functions and sending as message"""
	tabs += 1
	tabstr = '\t' * tabs
	if isinstance(data, str):
		output += tabstr + str(data) + "\n"	
	elif isinstance(data,tuple):
		output += tabstr + str(data) + "\n"	
	elif isinstance(data,list):
		output += tabstr + "[\n"	
		for item in data:
			output += deeplogdictstr(item, output, tabs+1)
		output += tabstr + "]\n"	
	elif isinstance(data,dict) or isinstance(data,AutoVivification):
		output += tabstr + "{\n"	
		for key, item in data.items():
			output += tabstr + str(key) + ": " 
			output += deeplogdictstr(item, output, tabs+1)
		output += tabstr + "}\n"
	else:
		output += tabstr + str(data) + "\n"		
	return output
		
def GetFileSize(filepath):
	size = os.stat(filepath).st_size
	return size

def get_directory_size(directory): # From https://www.thepythoncode.com/article/get-directory-size-in-bytes-using-python, accessed 08/11/2020
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def get_oldest_file(directory, _invert=False):
    """ Find and return the oldest file of input file names.
    Only one wins tie. Values based on time distance from present.
    Use of `_invert` inverts logic to make this a youngest routine,
    to be used more clearly via `get_youngest_file`.
    """
    files = list(os.scandir(directory))
    gt = operator.lt if _invert else operator.gt
    # Check for empty list.
    if not files:
        return None
    # Raw epoch distance.
    now = time.time()
    # Select first as arbitrary sentinel file, storing name and age.
    oldest = files[0], now - os.path.getctime(files[0])
    # Iterate over all remaining files.
    for f in files[1:]:
        age = now - os.path.getctime(f)
        if gt(age, oldest[1]):
            # Set new oldest.
            oldest = f, age
    # Return just the name of oldest file.
    return oldest[0]

nohupsize = 0

def clearfile(minsize=4, lastsend=False, tabs=0):
	""" Checks if the nohupout file is too big and sends it to me """
	global nohupsize
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of clearfile")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " minsize: " + str(minsize) + ", lastsend: " + TOGGLEFT[lastsend])
	global logfilepath
	
	minsize = minsize * 1024 * 1024
	maxsize = 8 * 1024 * 1024 # Max file size for discord is 8 mb
	
	# File paths
	nohup = ParentDir / ("nohup.out")
	paths = [logfilepath, nohup]
	ftype = ["log", "nohup"]
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Paths: " + str(paths))
	
	fileobjs = [] # List of files returns
	
	# Checking file size
	for num, file in enumerate(paths):
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Checking " + str(num))
		if Path.exists(file):
			logger.debug(tb(tabs+1) + "File exists")
			size = GetFileSize(file)
			logger.debug(tb(tabs+1) + "Size: " + str(size))
			if size < maxsize and (size > minsize or lastsend): 
				logger.debug(tb(tabs+1) + "Too big. Rotating")
				if num == 0:
					logger.debug(tb(tabs+1) + "Replacing log file")
					try:
						if lastsend: # Just send me the log file and delete it on bot close
							fileobjs.append(paths[0])
						else:
							# Replace the log file
							newlogfile = GenerateLogFile()
							logger.debug(tb(tabs+2) + "newlogfile: " + str(newlogfile))
							ResetHandler(logger, newlogfile)
							logger.debug(tb(tabs+2) + "Continued from: " + str(paths[0]))
							fileobjs.append(paths[0])
							logger.debug(tb(tabs+2) + "fileobjs now: " + str(fileobjs))
							logfilepath = newlogfile
						logger.debug(tb(tabs+1) + "Done")
					except Exception as e:
						edata = PrintException()
						print(edata)
				elif num == 1 and size > nohupsize:
					logger.debug(tb(tabs+1) + "Replacing nohup file")
					try:	
						newf = ParentDir / ("nohup " + datetime.now(timezone(MYTZ)).strftime(TFORMATDASHS) + ".txt")
						logger.debug(tb(tabs+2) + "Copying to " + str(newf))
						shutil.copyfile(file, newf)
						fileobjs.append(newf)
						logger.debug(tb(tabs+2) + "fileobjs now: " + str(fileobjs))
						logger.debug(tb(tabs+2) + "Opening nohup and clearing it")
						with open(file, "r+") as f:
							f.truncate(0)
						nohupsize = size
					except Exception as e:
						edata = PrintException()
						print(edata)
				
				logger.debug(tb(tabs+1) + "End of file handling")
			elif size > maxsize:
				logger.debug(tb(tabs+1) + "File got too big to send!")			
				newlogfile = GenerateLogFile()
				logger.debug(tb(tabs+2) + "newlogfile: " + str(newlogfile))
				ResetHandler(logger, newlogfile)
				logger.debug(tb(tabs+2) + "Continued from: " + str(paths[0]))
				fileobjs.append("Warning" + ftype[num])
				logger.debug(tb(tabs+2) + "fileobjs now: " + str(fileobjs))
				logfilepath = newlogfile
				
			else:
				logger.debug(tb(tabs+1) + "Too small to bother")
		else:
			logger.debug(tb(tabs+1) + "File doesn't exist?")
	
	if len(fileobjs):
		fileobjs = fileobjs + BackupDservers(tabs+1) # get the Dserver files
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " fileobjs: " + str(fileobjs))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " deleting a file if the directory has gotten too big")
	global DebugFilepath
	dirsize = get_directory_size(DebugFilepath)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " dirsize: " + str(dirsize))
	limit = 100 * 1024 * 1024 #100mbs
	if dirsize > limit:
		logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " directory has gotten too big")
		oldest = DebugFilepath / get_oldest_file(DebugFilepath)
		if oldest != None and oldest != logfilepath:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting oldest file: " + str(oldest))
			try:
				if Path.exists(oldest):
					Path.unlink(oldest)
			except Exception as e:
				edata = PrintException()
				print(edata)
		else:
			logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " No suitable file to delete " + str(oldest))
	
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of clearfile")			
	return fileobjs

def deletefiles(filelist, lastsend=False, tabs=0):
	""" Deletes the list of file paths given """
	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of deletefiles")
	tabs += 1
	for file in filelist:
		if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Deleting: " + str(file))
		try:
			if Path.exists(file):
				Path.unlink(file)
		except Exception as e:
			edata = PrintException()
			print(edata)
	if not lastsend: logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of deletefiles")

def GetUTCNowDTObj(tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetUTCNowDTObj")
	tabs+=1
	now = datetime.utcnow() # a datetime object of now, using the game's timezone
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now dtobj: " + str(now))
	return now

def GetUTCNowDTStr(thisformat=TFORMAT, tabs=0):
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of GetUTCNowDTObj")
	tabs+=1
	utc = pytz.timezone("UTC")
	now = datetime.now(utc) # a datetime object of now, using the game's timezone
	nowstr = now.strftime(thisformat)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now str: " + str(nowstr))
	return nowstr

def IsDateTimePassed(datetimeobj, tabs=0):
	""" Takes the datetimeobj, converts to UTC, and returns true/false if it has passed """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of IsDateTimePassed")
	tabs += 1
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " datetimeobj: " + str(datetimeobj))
	
	utc = timezone("UTC")
	converted = datetimeobj.astimezone(utc)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " converted: " + str(converted))
	
	now = datetime.utcnow()
	now = now.astimezone(utc)
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " now: " + str(now))
	
	result = False
	if converted < now:
		result = True

	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " result: " + TOGGLEFT[result])
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of IsDateTimePassed")
	return result
	
def BackupDservers(tabs=0):
	""" Returns a list of the Dserver files to send as backup """
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " Start of BackupDservers")
	tabs += 1
	dirf = ParentDir / "Dservers"
	logger.debug(tb(tabs+1) + "dirf: " + str(dirf))
	files = os.listdir(dirf)
	logger.debug(tb(tabs+1) + "files: " + str(files))
	fcopy = []
	maxsize = 8 * 1024 * 1024 # Max file size for discord is 8 mb
	for file in files:	
		if GetFileSize(dirf / file) < maxsize:
			fcopy.append(dirf / file)
	logger.debug(tb(tabs+1) + "fcopy: " + str(fcopy))
	logger.debug(tb(tabs) + str(inspect.getframeinfo(inspect.currentframe()).lineno) + " End of BackupDservers")
	return fcopy
	
def MergeDicts(dict1, dict2):
	""" Combines two dicts and returns them as a third
	Copied from https://www.geeksforgeeks.org/python-merging-two-dictionaries/ accessed 17/10/2020 """
	res = {**dict1, **dict2}
	return res
