#!/usr/bin/python

import collections
import json
import string
import ConfigParser

print "Content-Type: text/html"
print

config = ConfigParser.ConfigParser()
config.read("config.ini")
cpu_info_path = config.get("global", "cpu_info_path")

cpu_arr = collections.defaultdict()
try:
	with open(cpu_info_path, 'r'): pass
	proc_cpu = open(cpu_info_path, 'r')
	for line in proc_cpu:
		lines = line.strip()
		new_line = lines.split('\t: ')
		#cpu_arr[new_line[:1]] = new_line[1:]
		key = str(new_line[:1])[2:-2]
		key = key.replace("\\t", "")
		key = key.replace(" ", "_")
		value = str(new_line[1:])[2:-2]
		cpu_arr[key] = value
	proc_cpu.close()
except:
	cpu_arr['model_name'] = "unknown CPU"
	cpu_arr['cpu_MHz'] = "unknown speed"
	cpu_arr['cache_size'] = "unknown cache"

proc_cpu_json = json.dumps(cpu_arr)


#=== FIND AND REPLACE FOR RASPBERRY PI SPECIFIC CALLING
proc_cpu_json = proc_cpu_json.replace('Processor','model_name')
proc_cpu_json = proc_cpu_json.replace(' model_name', ' Processor')
proc_cpu_json = proc_cpu_json.replace('BogoMIPS','cpu_MHz')
#=== THERE WILL SURELY BE OTHERS ===================


proc_cpu_json = "["+proc_cpu_json+"]"
print "<p id=\"cpu_information\">" 
print proc_cpu_json 
print "</p>"

exit()