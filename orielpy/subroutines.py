import os
import orielpy
import psutil
import collections
import json
import string
import configparser
import decimal
import re
import time

from cherrystrap import database, logger
from operator import itemgetter

class subroutines:

    def static_subroutine(self):

        cpu_arr = {}

        fileName = orielpy.CPU_INFO_PATH

        # Account for condition where certain info is not available
        cpu_arr['model_name'] = "unknown CPU"
        cpu_arr['cpu_MHz'] = "unknown speed"
        cpu_arr['cache_size'] = "unknown cache"

        try:
            fileIn = open(fileName, 'r')
            lines = [line.rstrip() for line in fileIn]
            lines = [line for line in lines if line]
            for line in lines:
                new_line = line.split('\t: ')
                key = str(new_line[:1])[2:-2]
                key = key.replace("\\t", "")
                key = key.replace(" ", "_")
                value = str(new_line[1:])[2:-2]
                # Account for non-standard /proc/cpu (e.g. for ARM devices)
                if key == 'Processor':
                    key = 'model_name'
                elif key == ' model_name':
                    key = ' Processor'
                elif key == 'BogoMIPS':
                    key = 'cpu_MHz'
                cpu_arr[key] = value
            fileIn.close()
        except:
            logger.warn("Couldn't read CPU info from file %s" % fileName)


        return cpu_arr

    def diskio_subroutine(self):

        try:
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

            if orielpy.DISK_BLACKLIST.startswith('"') and orielpy.DISK_BLACKLIST.endswith('"'):
                diskBlacklist = orielpy.DISK_BLACKLIST[1:-1]
            else:
                diskBlacklist = orielpy.DISK_BLACKLIST
            disk_blacklist_exploded = diskBlacklist.split(',')
            disk_blacklist = [x.strip(' ') for x in disk_blacklist_exploded]

            for value in disk_partition_list:
                if ("sd" in value and len(value)==4):
                    check_value = str(value)[2]
                    try:
                        check_place = alphabet[check_value]
                    except:
                        check_place = 999
                elif any(x in value for x in disk_blacklist):
                    check_value = 999
                else:
                    check_place = 0

                if check_place <= orielpy.NUM_INTERNAL_DISK_CAPACITY:
                    internal_list.append(value)
                elif check_place == 24:
                    extraneous_list.append(value)
                elif check_place == 999:
                    volume_list.append(value)
                else:
                    external_list.append(value)

            # print 'Internal Volumes: %s<BR>' % internal_list
            # print 'External Volumes: %s<BR>' % external_list
            # print 'Comprehensive Volumes: %s<BR>' % volume_list
            # print 'Extraneous Volumes: %s<BR>' % extraneous_list

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

            list_of_strings = [str(s) for s in internal_disk_list]
            joined_string = " ".join(list_of_strings)
            logger.warn("%s" % joined_string)
            # print external_disk_list

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

                if readbytes < 0:
                    readbytes = 0
                if writebytes < 0:
                    writebytes = 0

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

                write_percent = ((float(writebytes) / 1048576) / orielpy.INTERNAL_DISK_MAX_RATE) * 100
                read_percent = ((float(readbytes) / 1048576) / orielpy.INTERNAL_DISK_MAX_RATE) * 100

                diskio_array['disk'] = key
                diskio_array['writebytes'] = writebytes_str
                diskio_array['readbytes'] = readbytes_str
                diskio_array['writePercent'] = str(int(write_percent))
                diskio_array['readPercent'] = str(int(read_percent))
                allinfo_array.append(diskio_array)

                for disk in internal_disk_list:
                    internal_list = {}
                    if disk in key:
                        internal_list['diskId'] = str(key)
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
                    external_list = {}
                    if disk in key:
                        external_list['diskId'] = str(key)
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
            #   int_disk.append(values['disk_id'])

            #print set(int_disk)

            int_final_list = []
            ext_final_list = []
            combined_final_list = []

            #print internal_disk_list

            keep_count = 1
            activity = False
            for disk in internal_disk_list:
                int_tot_list = {}
                if "sd" in disk:
                    check_value = str(disk)[2]
                    int_tot_list['diskId'] = "Internal Disk %s" % alphabet[check_value]
                else:
                    check_value = str(keep_count)
                    int_tot_list['diskId'] = "Internal Disk %s" % check_value
                for values in internal_array:
                    if disk in values['diskId']:
                        if str(values['activity']) !="0":
                            int_tot_list['status'] = values['status']
                            int_tot_list['activity'] = "100"
                            activity = True
                if not activity:
                    int_tot_list['status'] = "Idle"
                    int_tot_list['activity'] = "0"
                combined_final_list.append(int_tot_list)
                keep_count +=1

            keep_count = 1
            activity = False
            for disk in external_disk_list:
                ext_tot_list = {}
                if "sd" in disk:
                    check_value = str(disk)[2]
                    ext_tot_list['diskId'] = "External Disk %s" % alphabet[check_value]
                else:
                    check_value = str(keep_count)
                    ext_tot_list['diskId'] = "External Disk %s" % check_value
                for values in external_array:
                    if disk in values['diskId']:
                        if str(values['activity']) !="0":
                            ext_tot_list['status'] = values['status']
                            ext_tot_list['activity'] = "100"
                            activity = True
                if not activity:
                    ext_tot_list['status'] = "Idle"
                    ext_tot_list['activity'] = "0"
                combined_final_list.append(ext_tot_list)
                keep_count +=1

            combined_final_list = sorted(combined_final_list, key=itemgetter('diskId'))
        except:
            int_final_list = []
            ext_final_list = []
            combined_final_list = []
            logger.error("%s" % "There is a problem with psutil.disk_io_counters")

        #print combined_final_list

        return combined_final_list

    def sysfiles_subroutine(self):
        fans_temps = {}

        fileName = os.path.join(orielpy.PSEUDOFILE_FOLDER, orielpy.CPU_FAN_FILE)
        try:
            fileIn = open(fileName, 'r')
            fan1 = int(fileIn.read())
            fileIn.close()
        except:
            fan1 = 0

        fileName = os.path.join(orielpy.PSEUDOFILE_FOLDER, orielpy.SYS_FAN_FILE)
        try:
            fileIn = open(fileName, 'r')
            fan2 = int(fileIn.read())
            fileIn.close()
        except:
            fan2 = 0

        fileName = os.path.join(orielpy.PSEUDOFILE_FOLDER, orielpy.CPU_TEMP_FILE)

        try:
            fileIn = open(fileName, 'r')
            temp1 = float(fileIn.read())/1000
            fileIn.close()
        except:
            temp1 = 0

        fileName = os.path.join(orielpy.PSEUDOFILE_FOLDER, orielpy.SYS_TEMP_FILE)
        try:
            fileIn = open(fileName, 'r')
            temp3 = float(fileIn.read())/1000
            fileIn.close()
        except:
            temp3 = 0

        cpu_fan_percent = 100 * (float(fan1) - float(orielpy.CPU_FAN_MIN)) / (float(orielpy.CPU_FAN_MAX) - float(orielpy.CPU_FAN_MIN))
        sys_fan_percent = 100 * (float(fan2) - float(orielpy.SYS_FAN_MIN)) / (float(orielpy.SYS_FAN_MAX) - float(orielpy.SYS_FAN_MIN))
        cpu_temp_percent = 100 * (float(temp1) - float(orielpy.CPU_TEMP_MIN)) / (float(orielpy.CPU_TEMP_MAX) - float(orielpy.CPU_TEMP_MIN))
        sys_temp_percent = 100 * (float(temp3) - float(orielpy.SYS_TEMP_MIN)) / (float(orielpy.SYS_TEMP_MAX) - float(orielpy.SYS_TEMP_MIN))

        fans_temps['cpuTemp'] = str(int(temp1))
        fans_temps['sysTemp'] = str(int(temp3))
        fans_temps['cpuFan'] = str(int(fan1))
        fans_temps['sysFan'] = str(int(fan2))
        fans_temps['cpuTempPercent'] = str(int(cpu_temp_percent))
        fans_temps['cpuFanPercent'] = str(int(cpu_fan_percent))
        fans_temps['sysTempPercent'] = str(int(sys_temp_percent))
        fans_temps['sysFanPercent'] = str(int(sys_fan_percent))

        return fans_temps

    def cpuload_subroutine(self):
        cpu_list = []
        try:
            cpu_import = psutil.cpu_percent(interval=1, percpu=True)

            if type(cpu_import) is float:
                cpu_array = {}
                cpu_array['cpuPercent'] = str(int(cpu_import))
                cpu_list.append(cpu_array)
            else:
                cpu_index = 0
                while cpu_index < len(cpu_import):
                    cpu_array = {}
                    cpu_array['cpuPercent'] = str(int(cpu_import[cpu_index]))
                    cpu_list.append(cpu_array)
                    cpu_index +=1
        except:
            logger.error("%s" % "There is a problem with psutil.cpu_percent")

        return cpu_list
        #=====================================================

    def memload_subroutine(self):

        #PHYSICAL MEMORY=========================================
        mem_array = {}

        try:
            mem_total_raw = psutil.virtual_memory().total
            mem_mb = round(mem_total_raw / 1048576)
            mem_available_raw = psutil.virtual_memory().available
            mem_available = round(mem_available_raw / 1048576)
            mem_used = mem_mb - mem_available;
            mem_percent = psutil.virtual_memory().percent

            mem_array['memTotal'] = str(mem_mb)
            mem_array['memFree'] = str(mem_available)
            mem_array['memUsed'] = str(mem_used)
            mem_array['memPercent'] = str(int(mem_percent))

        except:
            logger.error("%s" % "There is a problem with psutil.virtual_memory")

        return mem_array
        #=====================================================

    def swapload_subroutine(self):
        #SWAP MEMORY=========================================
        swap_array = {}

        try:
            swap_total_raw = psutil.swap_memory().total
            swap_mb = round(swap_total_raw / 1048576)
            swap_available_raw = psutil.swap_memory().free
            swap_available = round(swap_available_raw / 1048576)
            swap_used = swap_mb - swap_available;
            swap_percent = psutil.swap_memory().percent

            swap_array['swapTotal'] = str(swap_mb)
            swap_array['swapFree'] = str(swap_available)
            swap_array['swapUsed'] = str(swap_used)
            swap_array['swapPercent'] = str(int(swap_percent))

        except:
            logger.error("%s" % "There is a problem with psutil.swap_memory")

        return swap_array
        #=====================================================

    def partitions_subroutine(self):

        #PARTITION INFO=========================================
        try:
            partition_import = psutil.disk_partitions(all=False)

            #print partition_import

            partition_index = 0
            partition_list = []
            if orielpy.VOLUME_BLACKLIST.startswith('"') and orielpy.VOLUME_BLACKLIST.endswith('"'):
                volumeBlacklist = orielpy.VOLUME_BLACKLIST[1:-1]
            else:
                volumeBlacklist = orielpy.VOLUME_BLACKLIST
            partition_blacklist_exploded = volumeBlacklist.split(',')
            partition_blacklist = [x.strip(' ') for x in partition_blacklist_exploded]

            while partition_index < len(partition_import):
                partition_array = {}
                mountpoint_temp = re.search('mountpoint=(.+?), fstype', str(partition_import[partition_index]))
                if mountpoint_temp:
                    mountpoint = str(mountpoint_temp.group(1))[1:-1]
                filesystem_temp = re.search('fstype=(.+?), opts', str(partition_import[partition_index]))
                if filesystem_temp:
                    filesystem = str(filesystem_temp.group(1))[1:-1]
                partition_array['mountpoint'] = mountpoint
                partition_array['filesystem'] = filesystem

                if (filesystem !="" and filesystem !="squashfs"):
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
                    if not any(x in mountpoint for x in partition_blacklist):
                        partition_list.append(partition_array)
                partition_index +=1

            partition_list = sorted(partition_list, key=itemgetter('mountpoint'))
        except:
            logger.error("%s" % "There is a problem with psutil.disk_partitions or psutil.disk_usage")

        return partition_list

        #=====================================================

    def networkload_subroutine(self):
        #NETWORK INFO=========================================
        networking_array = {}

        try:
            networking_sent_raw1 = psutil.net_io_counters(pernic=False).bytes_sent
            networking_received_raw1 = psutil.net_io_counters(pernic=False).bytes_recv
            time.sleep(1)
            networking_sent_raw2 = psutil.net_io_counters(pernic=False).bytes_sent
            networking_received_raw2 = psutil.net_io_counters(pernic=False).bytes_recv

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

            sent_saturation = 100 * (sent_Mbps / orielpy.NIC_READ_MAX)
            received_saturation = 100 * (received_Mbps / orielpy.NIC_WRITE_MAX)

            networking_array['uploadRate'] = str(sent_rate)
            networking_array['downloadRate'] = str(received_rate)
            networking_array['uploadPercent'] = str(int(sent_saturation))
            networking_array['downloadPercent'] = str(int(received_saturation))
        except:
            logger.error("%s" % "There is a problem with psutil.net_io_counters")

        return networking_array

    def syslogs_subroutine(self):

        log_files = []

        myDB = database.SQLite_DBConnection()
        log_kvs = myDB.select('SELECT * from logpaths ORDER BY program ASC')

        for entry in log_kvs:
            record = {}
            program = entry['Program']
            logpath = entry['LogPath']
            record['program'] = program
            record['logpath'] = logpath

            try:
                fileIn = open(logpath, 'r')
                lines = [line.rstrip() for line in fileIn]
                lines = [line for line in lines if line]
                record['logline'] = lines[len(lines)-1].replace("<","").replace(">","")
                fileIn.close()
            except:
                record['logline'] = "Log not available"

            log_files.append(record)

        return log_files


    def sysprocesses_subroutine(self):
        try:
            proc_import = psutil.pids()
            #print proc_import

            proc_prune = []
            for process in proc_import:
                proc_mem = psutil.Process(process).memory_info()
                if str(proc_mem) != "meminfo(rss=0, vms=0)":
                    proc_prune.append(process)

            #print proc_prune

            proc_tree = []
            for process in proc_prune:
                proc_array = {}
                if psutil.pid_exists(process):
                    load = psutil.Process(process).cpu_percent(interval=0.1)
                    if load != 0.0:
                        process_dict = psutil.Process(process)
                        process_info = process_dict.as_dict(attrs=["ppid", "name", "cmdline"])
                        proc_array['pid'] = process
                        proc_array['name'] = process_info['name']
                        proc_array['percent'] = str(load)+"%"
                        parent_id = process_info['ppid']
                        proc_array['ppid'] = parent_id
                        parent = psutil.Process(parent_id)
                        parent_info = parent.as_dict(attrs=["name"])
                        proc_array['parent'] = parent_info['name']
                        cmdList = process_info['cmdline']
                        processCommand = ' '.join(cmdList)
                        proc_array['cmd'] = processCommand
                        proc_tree.append(proc_array)

            if not proc_tree:
                proc_tree = []

        except:
            logger.error("%s" % "There is a problem with psutil.pids or psutil.memory_info")

        return proc_tree
