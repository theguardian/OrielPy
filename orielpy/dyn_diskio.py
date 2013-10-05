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
num_internal_disk_capacity = int(config.get("global", "num_internal_disk_capacity"))
internal_disk_max_rate = int(config.get("global", "internal_disk_max_rate"))
external_disk_max_rate = int(config.get("global", "external_disk_max_rate"))


#DISK I/O INFO=========================================
diskio_import1 = psutil.disk_io_counters(perdisk=True)
time.sleep(1)
diskio_import2 = psutil.disk_io_counters(perdisk=True)

disk_partition_list = []
internal_list = []
external_list = []
volume_list = []
extraneous_list = []

for key, value in diskio_import1.items():
    disk_partition_list.append(key)

alphabet = dict()
for index, letter in enumerate(string.ascii_lowercase):
	alphabet[letter] = index + 1

for value in disk_partition_list:
	if "sd" in value:
		check_value = str(value)[2]
		try:
			check_place = alphabet[check_value]
		except:
			check_place = 999
	elif value == "mmcblk0":
		check_place = 999
	elif "md" in value:
		check_place = 999
	else:
		check_place = 0
	if check_place <= num_internal_disk_capacity:
		internal_list.append(value)
	elif check_place == 24:
		extraneous_list.append(value)
	elif check_place == 999:
		volume_list.append(value)
	else:
		external_list.append(value)

#print 'Internal Volumes: %s<BR>' % internal_list
#print 'External Volumes: %s<BR>' % external_list
#print 'Comprehensive Volumes: %s<BR>' % volume_list
#print 'Extraneous Volumes: %s<BR>' % extraneous_list

internal_disk_list = []
external_disk_list = []

for value in internal_list:
	disk_non = value[:-1]
	internal_disk_list.append(disk_non)

for value in external_list:
	disk_non = value[:-1]
	external_disk_list.append(disk_non)

internal_disk_list = set(internal_disk_list)
external_disk_list = set(external_disk_list)

#print internal_disk_list
#print external_disk_list

num_internal_disks = len(internal_disk_list)
num_external_disks = len(external_disk_list)

#print num_internal_disks
#print num_external_disks

#===========================================================================
allinfo_array = []
internal_array = []
external_array = []

for key, value in diskio_import1.items():
	diskio_array = collections.defaultdict(list)
	readbytes_temp = re.search('read_bytes=(.+?), write', str(diskio_import1[key]))
	if readbytes_temp:
		readbytes = str(readbytes_temp.group(1))
	writebytes_temp = re.search('write_bytes=(.+?), read', str(diskio_import1[key]))
	if writebytes_temp:
		writebytes = str(writebytes_temp.group(1))
	readbytes = readbytes.replace("L", "")
	writebytes = writebytes.replace("L", "")
	readbytes1 = int(readbytes)
	writebytes1 = int(writebytes)

	readbytes_tempa = re.search('read_bytes=(.+?), write', str(diskio_import2[key]))
	if readbytes_tempa:
		readbytesa = str(readbytes_tempa.group(1))
	writebytes_tempa = re.search('write_bytes=(.+?), read', str(diskio_import2[key]))
	if writebytes_tempa:
		writebytesa = str(writebytes_tempa.group(1))
	readbytesa = readbytesa.replace("L", "")
	writebytesa = writebytesa.replace("L", "")
	readbytes2 = int(readbytesa)
	writebytes2 = int(writebytesa)

	readbytes = readbytes2 - readbytes1
	writebytes = writebytes2 - writebytes1

	readbytes_kb = float(readbytes) / 1024
	writebytes_kb = float(writebytes) / 1024
	if readbytes_kb > 1024:
		readbytes_mb = readbytes_kb / 1024
		readbytes_str = str("%.1f" % readbytes_mb)+" MB/s"
	else:
		readbytes_str = str("%.0f" % readbytes_kb)+" kB/s"
	if writebytes_kb > 1024:
		writebytes_mb = writebytes_kb / 1024
		writebytes_str = str("%.1f" % writebytes_mb)+" MB/s"
	else:
		writebytes_str = str("%.0f" % writebytes_kb)+" kB/s"

	write_percent = ((float(writebytes) / 1048576) / internal_disk_max_rate) * 100
	read_percent = ((float(readbytes) / 1048576) / internal_disk_max_rate) * 100

	diskio_array['disk'] = key
	diskio_array['writebytes'] = writebytes_str
	diskio_array['readbytes'] = readbytes_str
	diskio_array['write_percent'] = str(int(write_percent))
	diskio_array['read_percent'] = str(int(read_percent))
	allinfo_array.append(diskio_array)

	for disk in internal_disk_list:
		internal_list = collections.defaultdict(list)
		if disk in key:
			internal_list['disk_id'] = str(key)
			if readbytes !=0 and writebytes !=0:
				internal_list['status'] = "R/W on "+key
				internal_list['activity'] = "100"
			elif readbytes !=0 and writebytes ==0:
				internal_list['status'] = "Reading from "+key
				internal_list['activity'] = "100"
			elif readbytes ==0 and writebytes !=0:
				internal_list['activity'] = "100"
				internal_list['status'] = "Writing to "+key
			else:
				internal_list['status'] = "Idle"
				internal_list['activity'] = "0"
			internal_array.append(internal_list)

	for disk in external_disk_list:
		external_list = collections.defaultdict(list)
		if disk in key:
			external_list['disk_id'] = str(key)
			if readbytes !=0 and writebytes !=0:
				external_list['status'] = "R/W on "+key
				external_list['activity'] = "100"
			elif readbytes !=0 and writebytes ==0:
				external_list['status'] = "Reading from "+key
				external_list['activity'] = "100"
			elif readbytes ==0 and writebytes !=0:
				external_list['activity'] = "100"
				external_list['status'] = "Writing to "+key
			else:
				external_list['status'] = "Idle"
				external_list['activity'] = "0"
			external_array.append(external_list)

#print json.dumps(allinfo_array)
#print json.dumps(internal_array)
#print json.dumps(external_array)

#int_disk = []
#for values in internal_array:
#	int_disk.append(values['disk_id'])

#print set(int_disk)

int_final_list = []
ext_final_list = []

print internal_disk_list

keep_count = 1
for disk in internal_disk_list:
	int_tot_list = collections.defaultdict(list)
	if "sd" in disk:
		check_value = str(disk)[2]
		int_tot_list['disk_id'] = "Internal Disk %s" % alphabet[check_value]
	else:
		check_value = str(keep_count)
		int_tot_list['disk_id'] = "Internal Disk %s" % check_value
	for values in internal_array:
		if disk in values['disk_id']:
			if str(values['activity']) !="0":
				int_tot_list['status'] = values['status']
				int_tot_list['activity'] = "100"
	if not int_tot_list['activity']:
		int_tot_list['status'] = "Idle"
		int_tot_list['activity'] = "0"		
	int_final_list.append(int_tot_list)
	keep_count +=1

keep_count = 1
for disk in external_disk_list:
	ext_tot_list = collections.defaultdict(list)
	if "sd" in disk:
		check_value = str(disk)[2]
		ext_tot_list['disk_id'] = "External Disk %s" % alphabet[check_value]
	else:
		check_value = str(keep_count)
		ext_tot_list['disk_id'] = "External Disk %s" % check_value
	for values in external_array:
		if disk in values['disk_id']:
			if str(values['activity']) !="0":
				ext_tot_list['status'] = values['status']
				ext_tot_list['activity'] = "100"
	if not ext_tot_list['activity']:
		ext_tot_list['status'] = "Idle"
		ext_tot_list['activity'] = "0"		
	ext_final_list.append(ext_tot_list)
	keep_count +=1

disk_json = json.dumps(int_final_list)
ext_json = json.dumps(ext_final_list)


#====================================================================================


print "<p id=\"disk_summary\">" 
print disk_json 
print "</p>"
print "<p id=\"ext_summary\">" 
print ext_json 
print "</p>"
#=====================================================

exit()