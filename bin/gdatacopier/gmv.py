#!/usr/bin/env python

"""

	gmv
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
	print "gmv failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
except:
	print "gmv %s requires gdata-python-client v2.0+, fetch from Google at" % __version__
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
	Helpers
"""

def add_category_filter(document_query, docs_type):
	
	# If the user provided a doctype then add a filter
	if docs_type == "docs" or docs_type == "documents":
		document_query.categories.append('document')
	elif docs_type == "sheets" or docs_type == "spreadsheets":
		document_query.categories.append('spreadsheet')
	elif docs_type == "slides" or docs_type == "presentation":
		document_query.categories.append('presentation')
	elif docs_type == "folders":
		document_query.categories.append('folder')
	elif docs_type == "pdf":
		document_query.categories.append('pdf')

def add_title_match_filter(document_query, name_filter):
	
	# Add title match
	if not name_filter == None:
		if name_filter[len(name_filter) - 1: len(name_filter)] == "*":
			document_query['title-exact'] = 'false'
			document_query['title'] = name_filter[:len(name_filter) - 1]
		else:
			document_query['title-exact'] = 'true'
			document_query['title'] = name_filter
			
			
"""
	Checks to see if the desired folder exists
"""

def folder_name_exists(gd_client, folder_name):
	folder_name_query = gdata.docs.service.DocumentQuery(categories=['folder'], params={'showfolders': 'true'})
	# Destination folder must be an exact match
	add_title_match_filter(folder_name_query, folder_name.replace('*', ''))
	folder_feed = gd_client.Query(folder_name_query.ToUri())
	if folder_feed.entry: 
		return folder_feed.entry[0]
	return False

"""
	Makes a list of all documents that match the criteria and moves 
	them to the desired folder
"""
def move_documents(server_string, destination_folder, options):
	
	username, document_path = server_string.split(':', 1)
	
	# Counters for the moves
	success_counter = 0
	failure_counter = 0
	
	if not is_email(username):
		print "Usernames must be provided as your full Gmail address, hosted domains included."
		sys.exit(2)

	docs_type = None
	folder_name = None
	name_filter = None
	
	doc_param_parts = document_path.split('/')
	
	if len(doc_param_parts) > 1 and not (doc_param_parts[1] == '' or doc_param_parts[1] == '*'):
		docs_type = doc_param_parts[1]
		
	if len(doc_param_parts) > 2 and not (doc_param_parts[2] == '' or doc_param_parts[2] == '*'):
		folder_name = doc_param_parts[2]

	if len(doc_param_parts) > 3 and not (doc_param_parts[3] == '' or doc_param_parts[3] == '*'):
			name_filter = doc_param_parts[3]
			
	# Get a handle to the document list service
	sys.stdout.write("Logging into Google server as %s ... " % (username))
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")
	
	document_query = gdata.docs.service.DocumentQuery()
	
	add_category_filter(document_query, docs_type)

	# If the user provided a folder type then add this here
	if not folder_name == None and not folder_name == "all":
		document_query.AddNamedFolder(username, folder_name)

	add_title_match_filter(document_query, name_filter)
	
	try:
		# Authenticate to the document service'
		gd_client.ClientLogin(username, options.password)
		print "done."
		
		sys.stdout.write("Fetching document list feeds from Google servers for %s ... " % (username))
		feed = gd_client.Query(document_query.ToUri())
		print "done.\n"
		
		folder_resource = folder_name_exists(gd_client, destination_folder)
		
		for entry in feed.entry:
			
			sys.stdout.write("%-50s -m-> " % os.path.basename(entry.title.text)[-50:])

			try:
				if destination_folder == "/":
					gd_client.MoveOutOfFolder(entry)
				else:
					gd_client.MoveIntoFolder(entry, folder_resource)
					
				print "MOVED"
				success_counter = success_counter + 1
			except:
				print "FAILED."
				failure_counter = failure_counter + 1
				
	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
		sys.exit(2)
	except gdata.service.Error:
		print "Failed!"
		sys.exit(2)
	except gdata.service.CaptchaRequired:
		print "Captcha required, please login using the web interface and try again."
		sys.exit(2)
		
	print "\n%i success, %i failed" % (success_counter, failure_counter)


"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0

	
def parse_user_input():
	
	usage  = "usage: %prog [options] username@domain.com:/[doctype]/[foldername]/Title* [destination-folder]\n"
	usage += "              where [foldername] is the name of the folder you wish to create"
	parser = OptionParser(usage)

	parser.add_option('-s', '--silent', action = 'store_true', dest = 'silent', default = False,
						help = 'decreases verbosity, supresses all messages but summaries and critical errors')		
	parser.add_option('-p', '--password', dest = 'password',
						help = 'password for the user account, use with extreme caution. Could be stored in logs/history')
						
	(options, args) = parser.parse_args()

	greet(options)
	
	# arg1 must be a remote server string to fetch document lists
	
	if not len(args) == 2 or (not is_remote_server_string(args[0])):
		print "you most provide a remote server address as username@gmail.com:/[doctype]/[folder]"
		exit(1)

	if not len(args) == 2:
		print "you must provide a destination folder name, use / for root folder"
		exit(1)

	# If password not provided as part of the command line arguments, prompt the user
	# to enter the password on the command line

	if options.password == None: 
		options.password = getpass.getpass()

	move_documents(args[0], args[1], options)

# Prints Greeting
def greet(options):
	if not options.silent:
		print "gmv %s, folder creation utility. Copyright 2010 Eternity Technologies" % __version__
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