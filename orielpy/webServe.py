import os, cherrypy, urllib

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import threading, time

import collections
import json
import string
import ConfigParser
import decimal
import re

import orielpy
import lib.psutil as psutil

from orielpy import logger, formatter, database


def serve_template(templatename, **kwargs):

    interface_dir = os.path.join(str(orielpy.PROG_DIR), 'data/interfaces/')
    template_dir = os.path.join(str(interface_dir), orielpy.HTTP_LOOK)

    _hplookup = TemplateLookup(directories=[template_dir])

    try:
        template = _hplookup.get_template(templatename)
        return template.render(**kwargs)
    except:
        return exceptions.html_error_template().render()


class WebInterface(object):

    def index(self):
        raise cherrypy.HTTPRedirect("home")
    index.exposed=True

    def home(self):
        return serve_template(templatename="index.html", title="Home")
    home.exposed=True

    def config(self):
        http_look_dir = os.path.join(orielpy.PROG_DIR, 'data/interfaces/')
        http_look_list = [ name for name in os.listdir(http_look_dir) if os.path.isdir(os.path.join(http_look_dir, name)) ]

        config = {
                    "server_name":      orielpy.SERVER_NAME,
                    "http_host":        orielpy.HTTP_HOST,
                    "http_user":        orielpy.HTTP_USER,
                    "http_port":        orielpy.HTTP_PORT,
                    "http_pass":        orielpy.HTTP_PASS,
                    "http_look":        orielpy.HTTP_LOOK,
                    "http_look_list":   http_look_list,
                    "launch_browser":   int(orielpy.LAUNCH_BROWSER),
                    "logdir":           orielpy.LOGDIR,
                    "cpu_info_path":           orielpy.CPU_INFO_PATH,
                    "pseudofile_folder":           orielpy.PSEUDOFILE_FOLDER,
                    "num_internal_disk_capacity":           int(orielpy.NUM_INTERNAL_DISK_CAPACITY),
                    "sys_fan_file":           orielpy.SYS_FAN_FILE,
                    "sys_fan_min":           int(orielpy.SYS_FAN_MIN),
                    "sys_fan_max":           int(orielpy.SYS_FAN_MAX),
                    "cpu_fan_file":           orielpy.CPU_FAN_FILE,
                    "cpu_fan_min":           int(orielpy.CPU_FAN_MIN),
                    "cpu_fan_max":           int(orielpy.CPU_FAN_MAX),
                    "cpu_temp_file":           orielpy.CPU_TEMP_FILE,
                    "cpu_temp_min":           int(orielpy.CPU_TEMP_MIN),
                    "cpu_temp_max":           int(orielpy.CPU_TEMP_MAX),
                    "sys_temp_file":           orielpy.SYS_TEMP_FILE,
                    "sys_temp_min":           int(orielpy.SYS_TEMP_MIN),
                    "sys_temp_max":           int(orielpy.SYS_TEMP_MAX),
                    "nic_read_max":           int(orielpy.NIC_READ_MAX),
                    "nic_write_max":           int(orielpy.NIC_WRITE_MAX),
                    "internal_disk_max_rate":           int(orielpy.INTERNAL_DISK_MAX_RATE),
                    "external_disk_max_rate":           int(orielpy.EXTERNAL_DISK_MAX_RATE)
                }
        return serve_template(templatename="config.html", title="Settings", config=config)    
    config.exposed = True

    def configUpdate(self, server_name="Server", http_host='0.0.0.0', http_user=None, http_port=5151, http_pass=None, http_look=None, launch_browser=1, logdir=None, 
        cpu_info_path='/proc/cpuinfo', pseudofile_folder='/sys/devices/virtual/thermal/thermal_zone0/', num_internal_disk_capacity=0, sys_fan_file=None, sys_fan_min=0, sys_fan_max=5000, 
        cpu_fan_file=None, cpu_fan_min=0, cpu_fan_max=5000, cpu_temp_file='temp', cpu_temp_min=0, cpu_temp_max=100, sys_temp_file=None, 
        sys_temp_min=0, sys_temp_max=100, nic_read_max=200, nic_write_max=200, internal_disk_max_rate=200, external_disk_max_rate=200):

        orielpy.SERVER_NAME = server_name
        orielpy.HTTP_HOST = http_host
        orielpy.HTTP_PORT = http_port
        orielpy.HTTP_USER = http_user
        orielpy.HTTP_PASS = http_pass
        orielpy.HTTP_LOOK = http_look
        orielpy.LAUNCH_BROWSER = launch_browser
        orielpy.LOGDIR = logdir

        orielpy.CPU_INFO_PATH = cpu_info_path
        orielpy.PSEUDOFILE_FOLDER = pseudofile_folder
        orielpy.NUM_INTERNAL_DISK_CAPACITY = int(num_internal_disk_capacity)
        orielpy.SYS_FAN_FILE = sys_fan_file
        orielpy.SYS_FAN_MIN = int(sys_fan_min)
        orielpy.SYS_FAN_MAX = int(sys_fan_max)
        orielpy.CPU_FAN_FILE = cpu_fan_file
        orielpy.CPU_FAN_MIN = int(cpu_fan_min)
        orielpy.CPU_FAN_MAX = int(cpu_fan_max)
        orielpy.CPU_TEMP_FILE = cpu_temp_file
        orielpy.CPU_TEMP_MIN = int(cpu_temp_min)
        orielpy.CPU_TEMP_MAX = int(cpu_temp_max)
        orielpy.SYS_TEMP_FILE = sys_temp_file
        orielpy.SYS_TEMP_MIN = int(sys_temp_min)
        orielpy.SYS_TEMP_MAX = int(sys_temp_max)
        orielpy.NIC_READ_MAX = int(nic_read_max)
        orielpy.NIC_WRITE_MAX = int(nic_write_max)
        orielpy.INTERNAL_DISK_MAX_RATE = int(internal_disk_max_rate)
        orielpy.EXTERNAL_DISK_MAX_RATE = int(external_disk_max_rate)

        orielpy.config_write()

        raise cherrypy.HTTPRedirect("home")

    configUpdate.exposed = True

    def shutdown(self):
        orielpy.config_write()
        orielpy.SIGNAL = 'shutdown'
        message = 'shutting down ...'
        return serve_template(templatename="shutdown.html", title="Exit", message=message, timer=10)
        return page
    shutdown.exposed = True

    def restart(self):
        orielpy.SIGNAL = 'restart'
        message = 'restarting ...'
        return serve_template(templatename="shutdown.html", title="Restart", message=message, timer=10)
    restart.exposed = True

    def update_config(self):
        return serve_template(templatename="config.html", title="Config")
    update_config.exposed = True

    def static(self):

        cpu_arr = collections.defaultdict()
        try:
            with open(orielpy.CPU_INFO_PATH, 'r'): pass
            proc_cpu = open(orielpy.CPU_INFO_PATH, 'r')
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
        return "<p id=\"cpu_information\">"+proc_cpu_json+"</p>"
    static.exposed=True

    def diskio(self):
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
            if check_place <= orielpy.NUM_INTERNAL_DISK_CAPACITY:
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

            write_percent = ((float(writebytes) / 1048576) / orielpy.INTERNAL_DISK_MAX_RATE) * 100
            read_percent = ((float(readbytes) / 1048576) / orielpy.INTERNAL_DISK_MAX_RATE) * 100

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
        #   int_disk.append(values['disk_id'])

        #print set(int_disk)

        int_final_list = []
        ext_final_list = []

        #print internal_disk_list

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

        return "<p id=\"disk_summary\">"+disk_json+"</p><p id=\"ext_summary\">"+ext_json+"</p>"
    diskio.exposed=True

    def sysfiles(self):
        fans_temps = collections.defaultdict()

        try:
            with open(orielpy.PSEUDOFILE_FOLDER+orielpy.CPU_FAN_FILE, 'r'): pass
            fan1_file = open(orielpy.PSEUDOFILE_FOLDER+orielpy.CPU_FAN_FILE, 'r')
            fan1 = fan1_file.read()
            fan1_file.close()
        except:
            fan1 = 0
        fan1 = float(fan1)

        try:
            with open(orielpy.PSEUDOFILE_FOLDER+orielpy.SYS_FAN_FILE, 'r'): pass
            fan2_file = open(orielpy.PSEUDOFILE_FOLDER+orielpy.SYS_FAN_FILE, 'r')
            fan2 = fan2_file.read()
            fan2_file.close()
        except:
            fan2 = 0
        fan2 = float(fan2)

        try:
            with open(orielpy.PSEUDOFILE_FOLDER+orielpy.CPU_TEMP_FILE, 'r'): pass
            temp1_file = open(orielpy.PSEUDOFILE_FOLDER+orielpy.CPU_TEMP_FILE, 'r')
            temp1 = temp1_file.read()
            temp1_file.close()
        except:
            temp1 = 0
        temp1 = float(temp1) / 1000

        try:
            with open(orielpy.PSEUDOFILE_FOLDER+orielpy.SYS_TEMP_FILE, 'r'): pass
            temp3_file = open(orielpy.PSEUDOFILE_FOLDER+orielpy.SYS_TEMP_FILE, 'r')
            temp3 = temp3_file.read()
            temp3_file.close()
        except:
            temp3 = 0
        temp3 = float(temp3) / 1000

        cpu_fan_percent = 100 * (float(fan1) - float(orielpy.CPU_FAN_MIN)) / (float(orielpy.CPU_FAN_MAX) - float(orielpy.CPU_FAN_MIN))
        sys_fan_percent = 100 * (float(fan2) - float(orielpy.SYS_FAN_MIN)) / (float(orielpy.SYS_FAN_MAX) - float(orielpy.SYS_FAN_MIN))
        cpu1_temp_percent = 100 * (float(temp1) - float(orielpy.CPU_TEMP_MIN)) / (float(orielpy.CPU_TEMP_MAX) - float(orielpy.CPU_TEMP_MIN))
        sys_temp_percent = 100 * (float(temp3) - float(orielpy.SYS_TEMP_MIN)) / (float(orielpy.SYS_TEMP_MAX) - float(orielpy.SYS_TEMP_MIN))

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

        return "<p id=\"fans_temps_info\">"+fans_temps_json+"</p>"

    sysfiles.exposed=True

    def dynamic(self):
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

        #=====================================================

        #PARTITION INFO=========================================
        partition_import = psutil.disk_partitions(all=False)
        partition_array = collections.defaultdict()

        #print partition_import

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
            
        sent_saturation = 100 * (sent_Mbps / orielpy.NIC_READ_MAX)
        received_saturation = 100 * (received_Mbps / orielpy.NIC_WRITE_MAX)

        networking_array['upload_rate'] = str(sent_rate)
        networking_array['download_rate'] = str(received_rate)
        networking_array['upload_percent'] = str(int(sent_saturation))
        networking_array['download_percent'] = str(int(received_saturation))

        networking_json = json.dumps(networking_array)
        networking_json = "["+networking_json+"]"

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

        #=====================================================

        return "<p id=\"cpu_info\">"+cpu_json+"</p><p id=\"ram_info\">"+mem_json+"</p><p id=\"swap_info\">" +swap_json+"</p><p id=\"partition_info\">"+partition_json+"</p><p id=\"networking_info\">"+networking_json+"</p><p id=\"network_activity\">"+nw_json+"</p>" 
    dynamic.exposed=True

    def syslogs(self):

        log_files = collections.defaultdict()

        myDB = database.DBConnection()
        log_kvs = myDB.select('SELECT * from logpaths ORDER BY program ASC')

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

        return "<p id=\"log_files\">"+log_files_json+"</p>"
    syslogs.exposed=True

    def sysprocesses(self):
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

        return "<p id=\"running_process\">"+proc_json+"</p>"
    sysprocesses.exposed=True

    def update_logs(self):
        myDB = database.DBConnection()
        loglist = myDB.select('SELECT * from logpaths ORDER BY program ASC')
        return serve_template(templatename="update_logs.html", title="Update Logs", loglist=loglist)
    update_logs.exposed = True

    def add_remove_logs(self, action=None, program=None, logpath=None):
        myDB = database.DBConnection()

        if action == 'addlog':
            if len(program) !=0 and len(logpath) !=0:
                controlValueDict = {"Program": program}
                newValueDict = {
                    "LogPath":   logpath
                    }
                myDB.upsert("logpaths", newValueDict, controlValueDict)
        if action == 'removelog':
            myDB.select("DELETE from logpaths WHERE Program=?", [program])
        raise cherrypy.HTTPRedirect('home')
    add_remove_logs.exposed = True