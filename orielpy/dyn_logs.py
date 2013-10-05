#!/usr/bin/python

import re
import collections
import json
import string
import time
import ConfigParser

print "Content-Type: text/html"
print

config = ConfigParser.ConfigParser()
config.read("logs.ini")
log_kvs = config.items("global")
print log_kvs

log_files = collections.defaultdict()

for key, path in log_kvs:
	try:
		with open(path, 'r'): pass
		single_file = open(path, 'r')
		single_lines = [line.strip() for line in single_file]
		single_file.close()
		log_files[key] = single_lines[len(single_lines)-1]
	except:
		log_files[key] = "Log not available"
	

log_files_json = json.dumps(log_files)
log_files_json = "["+log_files_json+"]"

print "<p id=\"log_files\">" 
print log_files_json
print "</p>"

exit()