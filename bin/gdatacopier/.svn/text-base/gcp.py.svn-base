#!/usr/bin/env python

"""

	gcp
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
	import string
	import signal
	import time
	import stat
	import getpass
	import base64
except:
	print "gcp failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
	import gdata.spreadsheet.service
except:
	print "gcp %s requires gdata-python-client v2.0+, downloadable from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

# Accepted formats for exporting files, these have to be used as file extensions
__accepted_doc_formats__ = ['doc', 'html', 'zip', 'odt', 'pdf', 'png', 'rtf', 'txt']
__accepted_slides_formats__ = ['pdf', 'png', 'ppt', 'swf', 'txt', 'zip', 'html', 'odt']
__accepted_sheets_formats__ = ['xls', 'ods', 'txt', 'html', 'pdf', 'tsv', 'csv']
__bad_chars__ = ['\\', '/', '&', ':']

# Raised when more than one match of the document name is found
class DuplicateDocumentNameFound(Exception):
	pass

def signal_handler(signal, frame):
	    print "\n[Interrupted] Bye Bye!"
	    sys.exit(2)

"""
	Helpers
"""

# Strips characters that are not acceptable as file names
def sanatize_filename(filename):
	
	filename = filename.decode('UTF-8')
	for bad_char in __bad_chars__:
		filename = filename.replace(bad_char, '')
		
	filename = filename.lstrip().rstrip()
	return filename.encode(sys.getfilesystemencoding())


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

# If there's a filter for a title then this adds it on
def add_title_match_filter(document_query, name_filter):

	# Add title match
	if not name_filter == None:
		if name_filter[len(name_filter) - 1: len(name_filter)] == "*":
			document_query['title-exact'] = 'false'
			document_query['title'] = name_filter[:len(name_filter) - 1]
		else:
			document_query['title-exact'] = 'true'
			document_query['title'] = name_filter
			
# Gets an extension that works with a file format
def get_appropriate_extension(entry, docs_type, desired_format):
	
	entry_document_type = entry.GetDocumentType()
	
	# If docs_type is of specific type check for output format
	if docs_type == "docs" or docs_type == "documents" or entry.GetDocumentType() == "document":
		if __accepted_doc_formats__.count(desired_format) > 0: return desired_format
	elif docs_type == "sheets" or docs_type == "spreadsheets" or entry.GetDocumentType() == "spreadsheet":
		if __accepted_sheets_formats__.count(desired_format) > 0: return desired_format
	elif docs_type == "slides" or docs_type == "presentation" or entry.GetDocumentType() == "presentation":
		if __accepted_slides_formats__.count(desired_format) > 0: return desired_format
	elif docs_type == "pdf" and desired_format == "pdf":
		return "pdf"

	# If no docs_type it means there are a mixture of things being exported
	if desired_format == "oo" or docs_type == None:
		if entry_document_type == "document":
			return "odt"
		elif entry_document_type == "presentation":
			return "ppt"
		elif entry_document_type == "spreadsheet":
			return "ods"
		elif entry_document_type == "pdf":
			return "pdf"
	
	return None

def export_documents(source_path, target_path, options):
	
	if not os.path.isdir(target_path):
		print "%s does not exists or you don't have write privelleges" % target_path
		sys.exit(2)

	username, document_path = source_path.split(':')
	
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
		
		# Spreadsheet export requires separate authentication token
		spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
		spreadsheets_client.ClientLogin(username, options.password)
		
		print "done."

	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
		sys.exit(2)
	except gdata.service.CaptchaRequired:
		print "Captcha required, please login using the web interface and try again."
		sys.exit(2)
	except:
		print "Failed."
		sys.exit(2)
		
	# We must keep track of the docs token
	docs_auth_token = gd_client.GetClientLoginToken()
	sheets_auth_token = spreadsheets_client.GetClientLoginToken()
		
	if not options.silent:
		sys.stdout.write("Fetching document list feeds from Google servers for %s ... " % (username))
	
	feed = gd_client.Query(document_query.ToUri())
	
	if not options.silent:
		print "done.\n"
	
	# Counters
	success_counter = 0
	failed_counter = 0
	unchanged_counter = 0
	service_error_counter = 0
		
	for entry in feed.entry:

		export_extension = get_appropriate_extension(entry, docs_type, options.format)

		# Ignore export if the user hasn't provided a proper format
		if export_extension == None:
			print "%-30s -d-> WRONG FORMAT (%-30s)" % (entry.resourceId.text[0:30], entry.title.text[0:30])
			continue

		# Construct a file name for the export
		export_filename = None
		if not options.create_user_dir:
			export_filename = target_path + "/" + sanatize_filename(entry.title.text)
		else:
			if not os.path.isdir(target_path + "/" + entry.author[0].name.text):
				os.mkdir(target_path + "/" + entry.author[0].name.text)
				
			export_filename = target_path + "/" + entry.author[0].name.text + "/" + sanatize_filename(entry.title.text)
		
		# Add a Base64 hash of the resource id if the user requires it
		if options.add_document_id:
			export_filename = export_filename + "-" + base64.b64encode(entry.resourceId.text)
				
		export_filename = export_filename  + "." + export_extension
		
		# Tell the user something about what we are doing
		if not options.silent:
			sys.stdout.write("%-30s -d-> %-50s - " % (entry.resourceId.text[0:30], export_filename[-50:]))
				
		# Change authentication token if we are exporting spreadheets
		if entry.GetDocumentType() == "spreadsheet":
			gd_client.SetClientLoginToken(sheets_auth_token)
			
		# Thanks to http://stackoverflow.com/questions/127803/how-to-parse-iso-formatted-date-in-python
		# we are use regular expression to parse RFC3389
		updated_time = datetime.datetime(*map(int, re.split('[^\d]', entry.updated.text)[:-1]))
		remote_access_time = time.mktime(updated_time.timetuple())
			
		# If not force overwrite check if file exists and ask if we should overwrite
		if not options.overwrite and os.path.isfile(export_filename):
			user_answer = ""
			while not user_answer == "NO" and not user_answer.upper() == "YES":
				user_answer = raw_input("overwrite (yes/NO): ")
				if user_answer == "": user_answer = "NO"
			if user_answer == "NO": continue
			
		# If update then check to see if the datestamp has changed or ignore
		if options.update and os.path.isfile(export_filename):
			file_modified_time = os.stat(export_filename).st_mtime
			# If local file is older than remote file then download
			if file_modified_time >= remote_access_time:
				if not options.silent:
					print "UNCHANGED"
				unchanged_counter = unchanged_counter + 1
				continue

		try:
			gd_client.Export(entry, export_filename)
			os.utime(export_filename, (remote_access_time, remote_access_time))
			success_counter = success_counter + 1
			if not options.silent:
				print "OK"
		except gdata.service.Error:
			print "SERVICE ERROR"
			service_error_counter = service_error_counter + 1
		except:
			print "FAILED"
			failed_counter = failed_counter + 1
				
		gd_client.SetClientLoginToken(docs_auth_token)
		
	print "\n%i successful, %i unchanged, %i service error, %i failed" % (success_counter, unchanged_counter, service_error_counter, failed_counter)
	
	
def get_folder_entry(folder_name, gd_client):
	
	sys.stdout.write("Checking folder names on Google docs server ... ")
	document_query = gdata.docs.service.DocumentQuery()
	document_query.categories.append('folder')
	feed = gd_client.Query(document_query.ToUri())
	
	print "done."
	
	for entry in feed.entry:
		if entry.title.text == folder_name:
			return entry
			
	return None

# Searches for the name of the document through the 	
def get_document_resource(feed, document_name):
	for entry in feed.entry:
		if entry.title.text == document_name:
			return entry
	return None
	
def import_documents(source_path, target_path, options):
	
	upload_filenames = []
	username, document_path = target_path.split(':')
	
	# File or Directory add the names of the uploads to a list 
	if os.path.isdir(source_path):
		dir_list = os.listdir(source_path)
		for file_name in dir_list:
			if not file_name[:1] == ".": upload_filenames.append(source_path + "/" + file_name)
	elif os.path.isfile(source_path):
		upload_filenames.append(source_path)


	# Get a handle to the document list service
	sys.stdout.write("Logging into Google server as %s ... " % (username))
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")

	try:
		# Authenticate to the document service'
		gd_client.ClientLogin(username, options.password)
		print "done."

	except gdata.service.CaptchaRequired:
		print "Captcha required, please login using the web interface and try again."
		sys.exit(2)
	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
		sys.exit(2)
	except:
		print "Failed."
		sys.exit(2)

	# Upload folder name
	remote_folder = None
	doc_param_parts = document_path.split('/')

	if len(doc_param_parts) > 1 and not doc_param_parts[1] == '':
		# New line to make things look good
		print "\n"
		remote_folder = get_folder_entry(doc_param_parts[1], gd_client)
		if remote_folder == None:
			print "\nfolder name %s doesn't exists on your Google docs account" % doc_param_parts[1]
			sys.exit(2)
	
	# Counters
	notallowed_counter = 0
	failed_counter = 0
	dup_name_counter = 0
	updated_counter = 0
	success_counter = 0
	
	if not options.silent:
		sys.stdout.write("Fetching document list feeds from Google servers for %s ... " % (username))
	
	feed = gd_client.GetDocumentListFeed()
	
	if not options.silent:
		print "done.\n"
	
	# Upload allowed documents to the Google system
	for file_name in upload_filenames:
		
		extension = (file_name[len(file_name) - 4:]).upper()
		extension = extension.replace(".", "")

		if not options.silent:
			sys.stdout.write("%-50s -u-> " % os.path.basename(file_name)[-50:])
		
		# Check to see that we are allowed to upload this document
		if not extension in gdata.docs.service.SUPPORTED_FILETYPES:
			if not options.silent:
				print "NOT ALLOWED"
			notallowed_counter = notallowed_counter + 1
			continue

		mime_type = gdata.docs.service.SUPPORTED_FILETYPES[extension]
		media_source = gdata.MediaSource(file_path=file_name, content_type=mime_type)
		
		entry = None
		existing_resource = get_document_resource(feed, file_name)

		try:
			if existing_resource == None:
				if remote_folder == None:
					entry = gd_client.Upload(media_source, os.path.splitext(os.path.basename(file_name))[0])
				else:
					entry = gd_client.Upload(media_source, os.path.splitext(os.path.basename(file_name))[0], folder_or_uri=remote_folder)
			else:
				
				if not options.overwrite:
					user_answer = ""
					while not user_answer == "NO" and not user_answer.upper() == "YES":
						user_answer = raw_input("overwrite (yes/NO): ")
						if user_answer == "": user_answer = "NO"
					if user_answer == "NO": continue
				
				entry = gd_client.Put(media_source, existing_resource.GetEditMediaLink().href)
				updated_counter = updated_counter + 1
				
			success_counter = success_counter + 1
			
			"""
				Print new resource id or indicate that the document has been updated
			"""
			if existing_resource == None and not entry == None:
				print entry.resourceId.text
			else:
				print "UPDATED"


		except DuplicateDocumentNameFound:
			if not options.silent:
				print "DUPLICATE NAME"
			dup_name_counter = dup_name_counter + 1
		except:
			if not options.silent:
				print "FAILED"
			failed_counter = failed_counter + 1		

	print "\n%i successful, %i not allowed, %i failed, %i updated, %i duplicate names" % (success_counter, notallowed_counter, failed_counter, updated_counter, dup_name_counter)
	

"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0
	
def parse_user_input():
	
	usage = "usage: %prog [options] username@domain.com:/[doctype]/[folder]/Title* /home/directory"
	parser = OptionParser(usage)

	parser.add_option('-s', '--silent', action = 'store_true', dest = 'silent', default = False,
						help = 'decreases verbosity, supresses all messages but summaries and critical errors')	
	parser.add_option('-u', '--update', action = 'store_true', dest = 'update', default = False,
						help = 'only downloads files that have changed on the Google document servers, remote time stamps are replicated')
	parser.add_option('-o', '--overwrite', action = 'store_true', dest = 'overwrite', default = False,
						help = 'overwrite files if they already exists on the local disk (download only option)')
	parser.add_option('-i', '--doc-id', action = 'store_true', dest = 'add_document_id', default = False,
						help = 'appends document id at the end of the file name, use this if you have multiple documents with the same name')
	parser.add_option('-c', '--create-user-dir', action = 'store_true', dest = 'create_user_dir', default = False,
						help = 'copies documents to a sub-directory by owner name, if the directory doesn\'t exist it will be created')
	parser.add_option('-p', '--password', dest = 'password', 
						help = 'password to login to Google document servers, use with extreme caution, may be logged')
	parser.add_option('', '--password-file', dest = 'password_file', 
						help = 'password may alternatviely be read from a file, provide full path of file')
	parser.add_option('-f', '--format', default = 'oo',
						help = 'file format to export documents to, ensure to use default if exporting mixed types (download only option)')
						
	(options, args) = parser.parse_args()
	
	"""
		If arg1 is remote server then we are exporting documents, otherwise we are
		importing documents into the Google document system
	"""

	greet(options)
	
	if not sys.getfilesystemencoding():
		print "no encoding detected in your environment settings, try something like export LANG=en_US.UTF-8; "
		sys.exit(1)
	
	if not len(args) == 2:
		print "invalid or missing source or destination for copying documents"
		exit(1)
	
	document_source = args[0]
	document_target = args[1]

	if options.silent and not options.overwrite:
		print "overwrite option must be used when running in silent mode, include -o in your command"
		exit(1)
	
	"""
		Password may be provided from file, if a parameter is provided we will attempt to
		read this from the file
	"""
	
	if not options.password_file == None:
		try:
			options.password = open(options.password_file).read().strip()
		except:
			print "Failed to read password from file, ensure file exists with sufficient privelleges"
			sys.exit(2)
	
	"""
		If password not provided as part of the command line arguments, prompt the user
		to enter the password on the command line
	"""
	
	if options.password == None: 
		options.password = getpass.getpass()
	
	"""
		If the first parameter is a remote address we are backing up documents
		otherwise we are exporting documents to the Google servers. At this stage
		gcp does not support server to server or local to local copy of documents
	"""
	if is_remote_server_string(document_source) and is_remote_server_string(document_target):
		print "gcp does not support server-to-server transfer of documents, one of the locations must be local"
		exit(1)
	elif (not is_remote_server_string(document_source)) and (not is_remote_server_string(document_target)):
		print "gcp does not support local-to-local copying of files, please use cp"
		exit(1)
	elif is_remote_server_string(document_source) and (not is_remote_server_string(document_target)):
		export_documents(document_source, document_target, options)
	elif (not is_remote_server_string(document_source)) and is_remote_server_string(document_target):
		import_documents(document_source, document_target, options)
	else:
		print "gcp requires either the source or destination to be a remote address"
		exit(1)


# Prints Greeting
def greet(options):
	if not options.silent:
		print "gcp %s, document copy utility. Copyright 2010 Eternity Technologies" % __version__
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