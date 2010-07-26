#!/usr/bin/env python

"""

	gmkdir
	GDataCopier, http://gdatacopier.googlecode.com/
	
	Copyright 2010 Eternity Technologies.
	Distributed under the terms and conditions of the GNU/GPL v3
	
	GDataCopier is free software and comes with absolutely NO WARRANTY. Use 
	of this software is completely at YOUR OWN RISK.
	
	Version 2.1.1
		
"""

__version__ = "2.1.1"
__author__  = "Devraj Mukherjee"

"""
	Imports the required modules 
"""

try:
	from optparse import OptionParser
	import datetime
	import sys
	import os
	import re
	import signal
	import getpass
except:
	print "grm failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
except:
	print "gmkdir %s requires gdata-python-client v2.0+, fetch from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)


def signal_handler(signal, frame):
    print "\n[Interrupted] Bye Bye!"
    sys.exit(0)

"""
	Validate email address function courtsey using regular expressions
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65215
"""
def is_email(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

"""
	Checks to see if folder exists, otherwise creates it
"""
def make_folder(server_string, options):
	
	username, document_path = server_string.split(':', 1)
	doc_param_parts = document_path.split('/')
	
	if not is_email(username):
		print "Usernames must be provided as your full Gmail address, hosted domains included."
		sys.exit(2)
		
	if len(doc_param_parts) < 1:
		print "no folder name provided, aborting!"
		sys.exit(2)

	# Get a handle to the document list service
	sys.stdout.write("Logging into Google server as %s ... " % (username))
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")
	
	try:
		# Authenticate to the document service'
		gd_client.ClientLogin(username, options.password)
		print "done."
		
		document_query = gdata.docs.service.DocumentQuery()
		document_query.categories.append('folder')
		
		new_folder_name = doc_param_parts[1]
		
		sys.stdout.write("Fetching folder list feeds from Google servers for %s ... " % (username))
		feed = gd_client.Query(document_query.ToUri())
		print "done.\n"
		
		for entry in feed.entry:
			document_type = entry.GetDocumentType()
			
		folder_entry = gd_client.CreateFolder(new_folder_name)
		
	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
		sys.exit(2)
	except gdata.service.Error:
		print "Service Error - Failed!"
		sys.exit(2)
	except gdata.service.CaptchaRequired:
		print "Captcha required, please login using the web interface and try again."
		sys.exit(2)
	except:
		print "Failed."
		sys.exit(2)
		

"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0

	
def parse_user_input():
	
	usage  = "usage: %prog [options] username@domain.com:/[foldername]*\n"
	usage += "              where [foldername] is the name of the folder you wish to create"
	parser = OptionParser(usage)

	parser.add_option('-s', '--silent', action = 'store_true', dest = 'silent', default = False,
						help = 'decreases verbosity, supresses all messages but summaries and critical errors')		
	parser.add_option('-p', '--password', dest = 'password',
						help = 'password for the user account, use with extreme caution. Could be stored in logs/history')
						
	(options, args) = parser.parse_args()

	greet(options)
	
	# arg1 must be a remote server string to fetch document lists
	
	if not len(args) == 1 or (not is_remote_server_string(args[0])):
		print "you most provide a remote server address as username@gmail.com:/[foldername]"
		sys.exit(1)

	# If password not provided as part of the command line arguments, prompt the user
	# to enter the password on the command line

	if options.password == None: 
		options.password = getpass.getpass()

	make_folder(args[0], options)

# Prints Greeting
def greet(options):
	if not options.silent:
		print "gmkdir %s, folder creation utility. Copyright 2010 Eternity Technologies" % __version__
		print "Released under the GNU/GPL v3 at <http://gdatacopier.googlecode.com>\n"

# main() is where things come together, this joins all the messages defined above
# these messages must be executed in the defined order
def main():
	signal.signal(signal.SIGINT, signal_handler)
	parse_user_input()			# Check to see we have the right options or exit

# Begin execution of the main method since we are at the bottom of the script	
if __name__ == "__main__":
	main()
	
"""
	End of Python file
"""
