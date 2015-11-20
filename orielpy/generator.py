import shutil, os, datetime, urllib, urllib2, threading

from urllib import FancyURLopener

import orielpy
import json
import collections

from orielpy import database, logger, formatter, notifiers, subroutines
from subroutines import subroutines

def health(notify=True):

	health_list=[]
	error_msg=0
	myDB = database.DBConnection()
	subcall = subroutines()

	disk_json, ext_json = subcall.diskio_subroutine()
	sysfiles_json = subcall.sysfiles_subroutine()
	cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
	log_json = subcall.syslogs_subroutine()
	#process_json = subcall.sysprocesses_subroutine()

	json_disk = json.loads(disk_json)
	json_ext = json.loads(ext_json)
	json_sysfiles = json.loads(sysfiles_json)
	json_cpu = json.loads(cpu_json)
	json_mem = json.loads(mem_json)
	json_swap = json.loads(swap_json)
	json_partition = json.loads(partition_json)
	json_networking = json.loads(networking_json)
	json_nw = json.loads(nw_json)
	json_log = json.loads(log_json)
	#json_process = json.loads(process_json)


	rulelist = myDB.select('SELECT * from rules')
	for entries in rulelist:
		flag = entries['rule1']
		program = entries['rule2']
		condition = entries['rule3']
		comparison_value = entries['rule4']
		comparison_units = entries['rule5']
		message_rule = entries['rule6']
		custom_message = entries['rule7']
		if flag == "Log File":
			for key, value in json_log[0].iteritems():
				if key == program:
					prog_name = key
					log_string = value
			if condition == "Contains String":
				if comparison_value in log_string:
					messaging(message_rule, custom_message, prog_name+" log file contains ["+comparison_value+"]", notify, health_list)
					error_msg+=1
			elif condition == "Does Not Contain String":
				if comparison_value not in log_string:
					messaging(message_rule, custom_message, prog_name+" log file does not contain ["+comparison_value+"]", notify, health_list)
					error_msg+=1

		elif flag == "CPU Utilization":
			cpu_index = 0
			cpu_arr = []
			while cpu_index < len(json_cpu):
				cpu_arr.append(json_cpu[cpu_index]['cpu_percent'])
				cpu_index+=1
			cpu_value = max(cpu_arr)
			try:
				comparison_value = int(comparison_value)
				cpu_value = int(cpu_value)
			except:
				pass
			if condition == "Is Less Than":
				if comparison_value > cpu_value:
					messaging(message_rule, custom_message, "CPU utilization less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than":
				if comparison_value < cpu_value:
					messaging(message_rule, custom_message, "CPU utilization greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "CPU Temperature":
			for key, value in json_sysfiles[0].iteritems():
				if key == "cpu1_temp":
					cpu_temp = value
				elif key == "cpu1_temp_percent":
					cpu_temp_percent = value
			try:
				comparison_value = int(comparison_value)
				cpu_temp = int(cpu_temp)
				cpu_temp_percent = int(cpu_temp_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "Deg-C":
				if comparison_value > cpu_temp:
					messaging(message_rule, custom_message, "CPU temperature less than "+str(comparison_value)+" Deg-C", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Deg-C":
				if comparison_value < cpu_temp:
					messaging(message_rule, custom_message, "CPU temperature greater than "+str(comparison_value)+" Deg-C", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > cpu_temp_percent:
					messaging(message_rule, custom_message, "CPU temperature less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < cpu_temp_percent:
					messaging(message_rule, custom_message, "CPU temperature greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "System Temperature":
			for key, value in json_sysfiles[0].iteritems():
				if key == "sys_temp":
					sys_temp = value
				elif key == "sys_temp_percent":
					sys_temp_percent = value
			try:
				comparison_value = int(comparison_value)
				sys_temp = int(sys_temp)
				sys_temp_percent = int(sys_temp_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "Deg-C":
				if comparison_value > sys_temp:
					messaging(message_rule, custom_message, "System temperature less than "+str(comparison_value)+" Deg-C", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Deg-C":
				if comparison_value < sys_temp:
					messaging(message_rule, custom_message, "System temperature greater than "+str(comparison_value)+" Deg-C", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > sys_temp_percent:
					messaging(message_rule, custom_message, "System temperature less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < sys_temp_percent:
					messaging(message_rule, custom_message, "System temperature greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "CPU Fan Speed":
			for key, value in json_sysfiles[0].iteritems():
				if key == "cpu_fan":
					cpu_fan = value
				elif key == "cpu_fan_percent":
					cpu_fan_percent = value
			try:
				comparison_value = int(comparison_value)
				cpu_fan = int(cpu_fan)
				cpu_fan_percent = int(cpu_fan_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "RPM":
				if comparison_value > cpu_fan:
					messaging(message_rule, custom_message, "CPU fan speed less than "+str(comparison_value)+" RPM", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "RPM":
				if comparison_value < cpu_fan:
					messaging(message_rule, custom_message, "CPU fan speed greater than "+str(comparison_value)+" RPM", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > cpu_fan_percent:
					messaging(message_rule, custom_message, "CPU fan speed less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < cpu_fan_percent:
					messaging(message_rule, custom_message, "CPU fan speed greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "System Fan Speed":
			for key, value in json_sysfiles[0].iteritems():
				if key == "sys_fan":
					sys_fan = value
				elif key == "sys_fan_percent":
					sys_fan_percent = value
			try:
				comparison_value = int(comparison_value)
				sys_fan = int(sys_fan)
				sys_fan_percent = int(sys_fan_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "RPM":
				if comparison_value > sys_fan:
					messaging(message_rule, custom_message, "System fan speed less than "+str(comparison_value)+" RPM", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "RPM":
				if comparison_value < sys_fan:
					messaging(message_rule, custom_message, "System fan speed greater than "+str(comparison_value)+" RPM", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > sys_fan_percent:
					messaging(message_rule, custom_message, "System fan speed less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < sys_fan_percent:
					messaging(message_rule, custom_message, "System fan speed greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "Network Rx Rate":
			for key, value in json_networking[0].iteritems():
				if key == "download_rate":
					if "kB/s" in value:
						rx_rate = 0
					else:
						rx_rate = value.replace(" MB/s","")
				elif key == "download_percent":
					rx_percent = value
			try:
				comparison_value = float(comparison_value)
				rx_rate = float(rx_rate)
				rx_percent = float(rx_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "MB/s":
				if comparison_value > rx_rate:
					messaging(message_rule, custom_message, "Network Rx rate less than "+str(comparison_value)+" MB/s", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "MB/s":
				if comparison_value < rx_rate:
					messaging(message_rule, custom_message, "Network Rx rate greater than "+str(comparison_value)+" MB/s", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > rx_percent:
					messaging(message_rule, custom_message, "Network Rx rate less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < rx_percent:
					messaging(message_rule, custom_message, "Network Rx rate greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "Network Tx Rate":
			for key, value in json_networking[0].iteritems():
				if key == "upload_rate":
					if "kB/s" in value:
						tx_rate = 0
					else:
						tx_rate = value.replace(" MB/s","")
				elif key == "upload_percent":
					tx_percent = value
			try:
				comparison_value = float(comparison_value)
				tx_rate = float(tx_rate)
				tx_percent = float(tx_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "MB/s":
				if comparison_value > tx_rate:
					messaging(message_rule, custom_message, "Network Tx rate less than "+str(comparison_value)+" MB/s", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "MB/s":
				if comparison_value < tx_rate:
					messaging(message_rule, custom_message, "Network Tx rate greater than "+str(comparison_value)+" MB/s", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > tx_percent:
					messaging(message_rule, custom_message, "Network Tx rate less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < tx_percent:
					messaging(message_rule, custom_message, "Network Tx rate greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "RAM Free Space":
			for key, value in json_mem[0].iteritems():
				if key == "mem_free":
					mem_free = value
				elif key == "mem_percent":
					mem_percent = 100-int(value)
			try:
				comparison_value = int(comparison_value)
				mem_free = int(mem_free)
				mem_percent = int(mem_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "MB":
				if comparison_value > mem_free:
					messaging(message_rule, custom_message, "Free RAM less than "+str(comparison_value)+" MB", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "MB":
				if comparison_value < mem_free:
					messaging(message_rule, custom_message, "Free RAM greater than "+str(comparison_value)+" MB", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > mem_percent:
					messaging(message_rule, custom_message, "Free RAM less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < mem_percent:
					messaging(message_rule, custom_message, "Free RAM greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "Swap Memory Free Space":
			for key, value in json_swap[0].iteritems():
				if key == "swap_free":
					swap_free = value
				elif key == "swap_percent":
					swap_percent = 100-int(value)
			try:
				comparison_value = int(comparison_value)
				swap_free = int(swap_free)
				swap_percent = int(swap_percent)
			except:
				pass
			if condition == "Is Less Than" and comparison_units == "MB":
				if comparison_value > swap_free:
					messaging(message_rule, custom_message, "Free Swap Memory less than "+str(comparison_value)+" MB", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "MB":
				if comparison_value < swap_free:
					messaging(message_rule, custom_message, "Free Swap Memory greater than "+str(comparison_value)+" MB", notify, health_list)
					error_msg+=1
			elif condition == "Is Less Than" and comparison_units == "Percent":
				if comparison_value > swap_percent:
					messaging(message_rule, custom_message, "Free Swap Memory less than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1
			elif condition == "Is Greater Than" and comparison_units == "Percent":
				if comparison_value < swap_percent:
					messaging(message_rule, custom_message, "Free Swap Memory greater than "+str(comparison_value)+"%", notify, health_list)
					error_msg+=1

		elif flag == "Volume Free Space":
			volume_index = 0
			while volume_index < len(json_partition):
				volume = json_partition[volume_index]['mountpoint']
				if volume == program:
					volume_free = json_partition[volume_index]['free']
					if "MB" in volume_free:
						volume_free = volume_free.replace(" MB","")
						volume_units = "MB"
					elif "GB" in volume_free:
						volume_free = volume_free.replace(" GB","")
						volume_units = "GB"
					volume_percent = 100-int(json_partition[volume_index]['percent'])
					try:
						comparison_value = float(comparison_value)
						volume_free = float(volume_free)
						volume_percent = float(volume_percent)
					except:
						pass
					if condition == "Is Less Than" and comparison_units == "MB" and volume_units == "MB":
						if comparison_value > volume_free:
							messaging(message_rule, custom_message, volume+" free space less than "+str(comparison_value)+" MB", notify, health_list)
							error_msg+=1
					elif condition == "Is Greater Than" and comparison_units == "MB" and volume_units == "MB":
						if comparison_value < volume_free:
							messaging(message_rule, custom_message, volume+" free space greater than "+str(comparison_value)+" MB", notify, health_list)
							error_msg+=1
					elif condition == "Is Less Than" and comparison_units == "GB" and volume_units == "GB":
						if comparison_value > volume_free:
							messaging(message_rule, custom_message, volume+" free space less than "+str(comparison_value)+" GB", notify, health_list)
							error_msg+=1
					elif condition == "Is Greater Than" and comparison_units == "GB" and volume_units == "GB":
						if comparison_value < volume_free:
							messaging(message_rule, custom_message, volume+" free space greater than "+str(comparison_value)+" GB", notify, health_list)
							error_msg+=1
					elif condition == "Is Less Than" and comparison_units == "Percent":
						if comparison_value > volume_percent:
							messaging(message_rule, custom_message, volume+" free space less than "+str(comparison_value)+"%", notify, health_list)
							error_msg+=1
					elif condition == "Is Greater Than" and comparison_units == "Percent":
						if comparison_value < volume_percent:
							messaging(message_rule, custom_message, volume+" free space greater than "+str(comparison_value)+"%", notify, health_list)
							error_msg+=1
				volume_index+=1

		elif flag == "Disk Status":
			disk_index = 0
			while disk_index < len(json_disk):
				disk = json_disk[disk_index]['disk_id']
				if disk == program:
					disk_status = json_disk[disk_index]['status']
					if condition == "Is":
						if comparison_value == disk_status:
							messaging(message_rule, custom_message, disk+" is "+str(comparison_value), notify, health_list)
							error_msg+=1
					elif condition == "Is Not":
						if comparison_value != disk_status:
							messaging(message_rule, custom_message, disk+" is not "+str(comparison_value), notify, health_list)
							error_msg+=1
				disk_index+=1

			ext_index = 0
			while ext_index < len(json_ext):
				ext = json_ext[ext_index]['disk_id']
				if ext == program:
					ext_status = json_ext[ext_index]['status']
					if condition == "Is":
						if comparison_value == ext_status:
							messaging(message_rule, custom_message, ext+" is "+str(comparison_value), notify, health_list)
							error_msg+=1
					elif condition == "Is Not":
						if comparison_value != ext_status:
							messaging(message_rule, custom_message, ext+" is not "+str(comparison_value), notify, health_list)
							error_msg+=1
				ext_index+=1

	if error_msg == 0 and orielpy.NOTIFY_NOMINAL == 1:
		notifiers.notify_health(formatter.now()+": Server Status Nominal")

	if error_msg == 0:
		health_array = collections.defaultdict()
		health_array['status'] = "OK"
		health_list.append(health_array)
	else:
		health_array = collections.defaultdict()
		health_array['status'] = "WARN"
		health_list.append(health_array)

	health_json = json.dumps(health_list)
	return health_json

def messaging(message_rule=None, custom_message=None, notify_msg=None, notify=False, health_list=None):
		if message_rule == "Send Custom Message":
			notify_msg = custom_message
		else:
			notify_msg = notify_msg
		if notify:
			notifiers.notify_health(formatter.now()+": "+notify_msg)
			logger.warn("%s" % notify_msg)
		health_array = collections.defaultdict()
		health_array['warning'] = notify_msg
		health_list.append(health_array)
