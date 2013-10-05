#!/usr/bin/python

import psutil
import decimal
import re
import collections
import json
import string
import time
import ConfigParser

print "Content-Type: text/html"
print

config = ConfigParser.ConfigParser()
config.read("config.ini")
pseudofile_folder = config.get("global", "pseudofile_folder")
sys_fan_min = config.get("global", "sys_fan_min")
sys_fan_max = config.get("global", "sys_fan_max")
cpu_fan_min = config.get("global", "cpu_fan_min")
cpu_fan_max = config.get("global", "cpu_fan_max")
cpu_temp_min = config.get("global", "cpu_temp_min")
cpu_temp_max = config.get("global", "cpu_temp_max")
sys_temp_min = config.get("global", "sys_temp_min")
sys_temp_max = config.get("global", "sys_temp_max")
cpu_fan_file = config.get("global", "cpu_fan_file")
cpu_temp_file = config.get("global", "cpu_temp_file")
sys_fan_file = config.get("global", "sys_fan_file")
sys_temp_file = config.get("global", "sys_temp_file")

fans_temps = collections.defaultdict()

try:
	with open(pseudofile_folder+cpu_fan_file, 'r'): pass
	fan1_file = open(pseudofile_folder+cpu_fan_file, 'r')
	fan1 = fan1_file.read()
	fan1_file.close()
except:
	fan1 = 0
fan1 = float(fan1)

try:
	with open(pseudofile_folder+sys_fan_file, 'r'): pass
	fan2_file = open(pseudofile_folder+sys_fan_file, 'r')
	fan2 = fan2_file.read()
	fan2_file.close()
except:
	fan2 = 0
fan2 = float(fan2)

try:
	with open(pseudofile_folder+cpu_temp_file, 'r'): pass
	temp1_file = open(pseudofile_folder+cpu_temp_file, 'r')
	temp1 = temp1_file.read()
	temp1_file.close()
except:
	temp1 = 0
temp1 = float(temp1) / 1000

try:
	with open(pseudofile_folder+sys_temp_file, 'r'): pass
	temp3_file = open(pseudofile_folder+sys_temp_file, 'r')
	temp3 = temp3_file.read()
	temp3_file.close()
except:
	temp3 = 0
temp3 = float(temp3) / 1000

cpu_fan_percent = 100 * (float(fan1) - float(cpu_fan_min)) / (float(cpu_fan_max) - float(cpu_fan_min))
sys_fan_percent = 100 * (float(fan2) - float(sys_fan_min)) / (float(sys_fan_max) - float(sys_fan_min))
cpu1_temp_percent = 100 * (float(temp1) - float(cpu_temp_min)) / (float(cpu_temp_max) - float(cpu_temp_min))
sys_temp_percent = 100 * (float(temp3) - float(sys_temp_min)) / (float(sys_temp_max) - float(sys_temp_min))

fans_temps['cpu1_temp'] = str(int(temp1))
fans_temps['sys_temp'] = str(int(temp3))
fans_temps['cpu_fan'] = str(int(fan1))
fans_temps['sys_fan'] = str(int(fan2))
fans_temps['cpu1_temp_percent'] = str(int(cpu1_temp_percent))
fans_temps['cpu_fan_percent'] = str(int(cpu_fan_percent))
fans_temps['sys_temp_percent'] = str(int(sys_temp_percent))
fans_temps['sys_fan_percent'] = str(int(sys_fan_percent))

fans_temps_json = json.dumps(fans_temps)
fans_temps_json = "["+fans_temps_json+"]"

print "<p id=\"fans_temps_info\">" 
print fans_temps_json 
print "</p>"

exit()