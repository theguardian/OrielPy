import shutil, os, datetime, urllib, urllib2, threading

from urllib import FancyURLopener

import orielpy
import json
import collections

from cherrystrap import database, logger, formatter
from orielpy import notifiers
from orielpy.subroutines import subroutines

def health(notify=True):

	health_list=[]
	error_msg=0
	myDB = database.SQLite_DBConnection()
	subcall = subroutines()

	json_disk = subcall.diskio_subroutine()
	json_sysfiles = subcall.sysfiles_subroutine()
	json_cpu = subcall.cpuload_subroutine()
	json_mem = subcall.memload_subroutine()
	json_swap = subcall.swapload_subroutine()
	json_partition = subcall.partitions_subroutine()
	json_networking = subcall.networkload_subroutine()
	json_log = subcall.syslogs_subroutine()
	#process_json = subcall.sysprocesses_subroutine()

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
			try:
				for logline in json_log:
					if logline['program'] == program:
						prog_name = logline['program']
						log_string = logline['logline']
						if condition == "Contains String":
							if comparison_value in log_string:
								messaging(message_rule, custom_message, prog_name+" log file contains ["+comparison_value+"]", notify, health_list)
								error_msg+=1
						elif condition == "Does Not Contain String":
							if comparison_value not in log_string:
								messaging(message_rule, custom_message, prog_name+" log file does not contain ["+comparison_value+"]", notify, health_list)
								error_msg+=1
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of log file/s")

		elif flag == "CPU Utilization":
			try:
				cpu_index = 0
				cpu_arr = []
				while cpu_index < len(json_cpu):
					cpu_arr.append(json_cpu[cpu_index]['cpuPercent'])
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of CPU utilization")

		elif flag == "CPU Temperature":
			try:
				for key, value in json_sysfiles.iteritems():
					if key == "cpuTemp":
						cpu_temp = value
					elif key == "cpuTempPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of CPU temperature")

		elif flag == "System Temperature":
			try:
				for key, value in json_sysfiles.iteritems():
					if key == "sysTemp":
						sys_temp = value
					elif key == "sysTempPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of system temperature")

		elif flag == "CPU Fan Speed":
			try:
				for key, value in json_sysfiles.iteritems():
					if key == "cpuFan":
						cpu_fan = value
					elif key == "cpuFanPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of CPU fan speed")

		elif flag == "System Fan Speed":
			try:
				for key, value in json_sysfiles.iteritems():
					if key == "sysFan":
						sys_fan = value
					elif key == "sysFanPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of system fan speed")

		elif flag == "Network Rx Rate":
			try:
				for key, value in json_networking.iteritems():
					if key == "downloadRate":
						if "kB/s" in value:
							rx_rate = 0
						else:
							rx_rate = value.replace(" MB/s","")
					elif key == "downloadPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of network Rx rate")

		elif flag == "Network Tx Rate":
			try:
				for key, value in json_networking.iteritems():
					if key == "uploadRate":
						if "kB/s" in value:
							tx_rate = 0
						else:
							tx_rate = value.replace(" MB/s","")
					elif key == "uploadPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of network Tx rate")

		elif flag == "RAM Free Space":
			try:
				for key, value in json_mem.iteritems():
					if key == "memFree":
						mem_free = value
					elif key == "memPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of RAM free space")

		elif flag == "Swap Memory Free Space":
			try:
				for key, value in json_swap.iteritems():
					if key == "swapFree":
						swap_free = value
					elif key == "swapPercent":
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of swap memory free space")

		elif flag == "Volume Free Space":
			try:
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
			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of volume free space")

		elif flag == "Disk Status":
			try:
				disk_index = 0
				while disk_index < len(json_disk):
					disk = json_disk[disk_index]['diskId']
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

			except:
				error_msg+=1
				logger.error("%s" % "There is a problem finding health of disk status")

	if error_msg == 0 and orielpy.NOTIFY_NOMINAL == 1:
		notifiers.notify_health(formatter.now()+": Server Status Nominal")

	if error_msg == 0:
		health_array = collections.defaultdict()
		health_array['status'] = "success"
		health_list.append(health_array)
	else:
		health_array = collections.defaultdict()
		health_array['status'] = "warning"
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
