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
nic_write_max = int(config.get("global", "nic_write_max"))
nic_read_max = int(config.get("global", "nic_read_max"))

#CPU PERCENT=========================================
cpu_import = psutil.cpu_percent(interval=1, percpu=True)

if type(cpu_import) is float:
	cpu_array = collections.defaultdict()
	cpu_array['cpu_percent'] = str(int(cpu_import))
	cpu_json = json.dumps(cpu_array)
	cpu_json = "["+cpu_json+"]"
else:
	cpu_index = 0
	cpu_list = []
	while cpu_index < len(cpu_import):
		cpu_array = collections.defaultdict()
		cpu_array['cpu_percent'] = str(int(cpu_import[cpu_index]))
		cpu_list.append(cpu_array)
		cpu_index +=1		
	cpu_json = json.dumps(cpu_list)

print "<p id=\"cpu_info\">" 
print cpu_json 
print "</p>"
#=====================================================

#PHYSICAL MEMORY=========================================
mem_array = collections.defaultdict()

mem_total_raw = psutil.virtual_memory().total
mem_mb = mem_total_raw / 1048576
mem_available_raw = psutil.virtual_memory().available
mem_available = mem_available_raw / 1048576
mem_used = mem_mb - mem_available;
mem_percent = psutil.virtual_memory().percent

mem_array['mem_total'] = str(mem_mb)
mem_array['mem_free'] = str(mem_available)
mem_array['mem_used'] = str(mem_used)
mem_array['mem_percent'] = str(int(mem_percent))

mem_json = json.dumps(mem_array)
mem_json = "["+mem_json+"]"

print "<p id=\"ram_info\">" 
print mem_json 
print "</p>"
#=====================================================

#SWAP MEMORY=========================================
swap_array = collections.defaultdict()

swap_total_raw = psutil.swap_memory().total
swap_mb = swap_total_raw / 1048576
swap_available_raw = psutil.swap_memory().free
swap_available = swap_available_raw / 1048576
swap_used = swap_mb - swap_available;
swap_percent = psutil.swap_memory().percent

swap_array['swap_total'] = str(swap_mb)
swap_array['swap_free'] = str(swap_available)
swap_array['swap_used'] = str(swap_used)
swap_array['swap_percent'] = str(int(swap_percent))

swap_json = json.dumps(swap_array)
swap_json = "["+swap_json+"]"

print "<p id=\"swap_info\">" 
print swap_json 
print "</p>"
#=====================================================

#PARTITION INFO=========================================
partition_import = psutil.disk_partitions(all=False)
partition_array = collections.defaultdict()

print partition_import

partition_index = 0
partition_list = []
while partition_index < len(partition_import):
	partition_array = collections.defaultdict()
	mountpoint_temp = re.search('mountpoint=(.+?), fstype', str(partition_import[partition_index]))
	if mountpoint_temp:
		mountpoint = str(mountpoint_temp.group(1))[1:-1]
	filesystem_temp = re.search('fstype=(.+?), opts', str(partition_import[partition_index]))
	if filesystem_temp:
		filesystem = str(filesystem_temp.group(1))[1:-1]
	partition_array['mountpoint'] = mountpoint
	partition_array['filesystem'] = filesystem
	
	if filesystem !="":
		disk_total_raw = psutil.disk_usage(mountpoint).total
		disk_total_MB = float(disk_total_raw) / 1048576
		if disk_total_MB > 1024:
			disk_total = disk_total_MB / 1024
			disk_total = str("%.1f" % disk_total)+" GB"
		else:
			disk_total = disk_total_MB
			disk_total = str("%.0f" % disk_total)+" MB"
		partition_array['total'] = disk_total
	
		disk_used_raw = psutil.disk_usage(mountpoint).used
		disk_used_MB = float(disk_used_raw) / 1048576
		if disk_used_MB > 1024:
			disk_used = disk_used_MB / 1024
			disk_used = str("%.1f" % disk_used)+" GB"
		else:
			disk_used = disk_used_MB
			disk_used = str("%.0f" % disk_used)+" MB"
		partition_array['used'] = disk_used
	
		disk_free_raw = psutil.disk_usage(mountpoint).free
		disk_free_MB = float(disk_free_raw) / 1048576
		if disk_free_MB > 1024:
			disk_free = disk_free_MB / 1024
			disk_free = str("%.1f" % disk_free)+" GB"
		else:
			disk_free = disk_free_MB
			disk_free = str("%.0f" % disk_free)+" MB"
		partition_array['free'] = disk_free
	
		disk_percent_raw = psutil.disk_usage(mountpoint).percent
		disk_percent = str(int(disk_percent_raw))
		partition_array['percent'] = disk_percent
	
		partition_list.append(partition_array)
	partition_index +=1		
partition_json = json.dumps(partition_list)

print "<p id=\"partition_info\">" 
print partition_json 
print "</p>"
#=====================================================

#NETWORK INFO=========================================
networking_array = collections.defaultdict()

networking_sent_raw1 = psutil.network_io_counters(pernic=False).bytes_sent
networking_received_raw1 = psutil.network_io_counters(pernic=False).bytes_recv
time.sleep(1)
networking_sent_raw2 = psutil.network_io_counters(pernic=False).bytes_sent
networking_received_raw2 = psutil.network_io_counters(pernic=False).bytes_recv

sent_Bps = networking_sent_raw2 - networking_sent_raw1
received_Bps = networking_received_raw2 - networking_received_raw1

sent_Kbps = float(sent_Bps) / 1024
received_Kbps = float(received_Bps) / 1024

sent_Mbps = float(sent_Kbps) / 1024
received_Mbps = float(received_Kbps) / 1024

if sent_Kbps > 1024:
	sent_speed = sent_Kbps / 1024
	sent_rate = str("%.1f" % sent_speed)+" MB/s"
else:
	sent_speed = sent_Kbps
	sent_rate = str("%.0f" % sent_speed)+" kB/s"
	
if received_Kbps > 1024:
	received_speed = received_Kbps / 1024
	received_rate = str("%.1f" % received_speed)+" MB/s"
else:
	received_speed = received_Kbps
	received_rate = str("%.0f" % received_speed)+" kB/s"
	
sent_saturation = 100 * (sent_Mbps / nic_read_max)
received_saturation = 100 * (received_Mbps / nic_write_max)

networking_array['upload_rate'] = str(sent_rate)
networking_array['download_rate'] = str(received_rate)
networking_array['upload_percent'] = str(int(sent_saturation))
networking_array['download_percent'] = str(int(received_saturation))

networking_json = json.dumps(networking_array)
networking_json = "["+networking_json+"]"

print "<p id=\"networking_info\">" 
print networking_json 
print "</p>"

network_activity = collections.defaultdict()
network_activity['name'] = "Network"
if int(sent_Bps) == 0 and int(received_Kbps) == 0:
	network_activity['status'] = "Idle"
	network_activity['activity'] = "0"
else:
	network_activity['status'] = "Active"
	network_activity['activity'] = "100"

nwtemp_json = json.dumps(network_activity)
nw_json = "["+nwtemp_json+"]"

print "<p id=\"network_activity\">" 
print nw_json 
print "</p>"

#=====================================================

exit()