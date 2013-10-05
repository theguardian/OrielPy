#!/usr/bin/python

import psutil
import re
import collections
import json
import string
import time
import ConfigParser

print "Content-Type: text/html"
print

proc_import = psutil.get_pid_list()
#print proc_import

proc_prune = []
for process in proc_import:
	proc_mem = psutil.Process(process).get_memory_info()
	if str(proc_mem) != "meminfo(rss=0, vms=0)":
		proc_prune.append(process)

#print proc_prune

proc_tree = []
for process in proc_prune:
	proc_array = collections.defaultdict()
	if psutil.pid_exists(process):
		load = psutil.Process(process).get_cpu_percent(interval=0.1)
		if load != 0.0:
			proc_array['pid'] = process
			proc_array['name'] = psutil.Process(process).name
			proc_array['percent'] = load
			parent = psutil.Process(process).ppid
			proc_array['ppid'] = parent
			proc_array['parent'] = psutil.Process(parent).name
			cmd_state = psutil.Process(process).cmdline
			proc_array['cmd'] = cmd_state
			proc_tree.append(proc_array)

if not proc_tree:
	proc_array = collections.defaultdict()
	proc_array['pid'] = 0
	proc_tree.append(proc_array)

proc_json = json.dumps(proc_tree)

print "<p id=\"running_process\">" 
print proc_json
print "</p>"


exit()