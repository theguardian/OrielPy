import os, cherrypy, urllib

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import threading, time

import orielpy

from orielpy import logger, formatter, database, notifiers, subroutines, generator
from subroutines import subroutines

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

    def update_config(self):
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
                    "verify_ssl":   int(orielpy.VERIFY_SSL),
                    "launch_browser":   int(orielpy.LAUNCH_BROWSER),
                    "logdir":           orielpy.LOGDIR,
                    "notification_frequency":   orielpy.NOTIFICATION_FREQUENCY,
                    "notification_units":   orielpy.NOTIFICATION_UNITS,
                    "notify_nominal":   orielpy.NOTIFY_NOMINAL,
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
                    "external_disk_max_rate":           int(orielpy.EXTERNAL_DISK_MAX_RATE),
                    "use_twitter" :     orielpy.USE_TWITTER,
                    "twitter_username" :     orielpy.TWITTER_USERNAME,
                    "twitter_password" :     orielpy.TWITTER_PASSWORD,
                    "twitter_prefix" :     orielpy.TWITTER_PREFIX
                }

        myDB = database.DBConnection()
        loglist = myDB.select('SELECT * from logpaths ORDER BY program ASC')
        rulelist = myDB.select('SELECT * from rules ORDER BY id_num ASC')
        subcall = subroutines()
        disk_json, ext_json = subcall.diskio_subroutine()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return serve_template(templatename="config.html", title="Config", config=config, loglist=loglist, rulelist=rulelist, volumes=partition_json, disk=disk_json, ext=ext_json)
    update_config.exposed = True

    def generalUpdate(self, server_name="Server", http_host='0.0.0.0', http_user=None, http_port=5151, http_pass=None, http_look=None,
        verify_ssl=1, launch_browser=0, logdir=None,
        notification_frequency=0, notification_units='Hours', notify_nominal=0):

        if verify_ssl == "on":
            verify_ssl = 1
        else:
            verify_ssl = 0

        if launch_browser == "on":
            launch_browser = 1
        else:
            launch_browser = 0

        if notify_nominal == "on":
            notify_nominal = 1
        else:
            notify_nominal = 0

        orielpy.SERVER_NAME = server_name
        orielpy.HTTP_HOST = http_host
        orielpy.HTTP_PORT = http_port
        orielpy.HTTP_USER = http_user
        orielpy.HTTP_PASS = http_pass
        orielpy.HTTP_LOOK = http_look
        orielpy.VERIFY_SSL = verify_ssl
        orielpy.LAUNCH_BROWSER = launch_browser
        orielpy.LOGDIR = logdir
        orielpy.NOTIFICATION_FREQUENCY = int(notification_frequency)
        orielpy.NOTIFICATION_UNITS = notification_units
        orielpy.NOTIFY_NOMINAL = notify_nominal

        orielpy.config_write()

        raise cherrypy.HTTPRedirect("home")

    generalUpdate.exposed = True

    def serverUpdate(self,
        cpu_info_path='/proc/cpuinfo', pseudofile_folder='/sys/devices/virtual/thermal/thermal_zone0/', num_internal_disk_capacity=0, sys_fan_file=None, sys_fan_min=0, sys_fan_max=5000,
        cpu_fan_file=None, cpu_fan_min=0, cpu_fan_max=5000, cpu_temp_file='temp', cpu_temp_min=0, cpu_temp_max=100, sys_temp_file=None,
        sys_temp_min=0, sys_temp_max=100, nic_read_max=200, nic_write_max=200, internal_disk_max_rate=200, external_disk_max_rate=200):

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

    serverUpdate.exposed = True

    def notifyUpdate(self, use_twitter=0, twitter_username=None, twitter_password=None,
        twitter_prefix='OrielPy'):

        if use_twitter == "on":
            use_twitter = 1
        else:
            use_twitter = 0

        orielpy.USE_TWITTER = use_twitter
        orielpy.TWITTER_USERNAME = twitter_username
        orielpy.TWITTER_PASSWORD = twitter_password
        orielpy.TWITTER_PREFIX = twitter_prefix

        orielpy.config_write()

        raise cherrypy.HTTPRedirect("home")

    notifyUpdate.exposed = True

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

    def notify(self):
        return serve_template(templatename="notify_config.html", title="Configure Notifications")
    notify.exposed = True

    def static(self):
        subcall = subroutines()
        return subcall.static_subroutine()
    static.exposed=True

    def diskio_internal(self):
        subcall = subroutines()
        disk_json, ext_json = subcall.diskio_subroutine()
        return disk_json
    diskio_internal.exposed=True

    def diskio_external(self):
        subcall = subroutines()
        disk_json, ext_json = subcall.diskio_subroutine()
        return ext_json
    diskio_external.exposed=True

    def processors(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return cpu_json
    processors.exposed=True

    def memory(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return mem_json
    memory.exposed=True

    def swap(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return swap_json
    swap.exposed=True

    def partitions(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return partition_json
    partitions.exposed=True

    def network(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return networking_json
    network.exposed=True

    def activity(self):
        subcall = subroutines()
        cpu_json, mem_json, swap_json, partition_json, networking_json, nw_json = subcall.dynamic_subroutine()
        return nw_json
    activity.exposed=True

    def sysfiles(self):
        subcall = subroutines()
        return subcall.sysfiles_subroutine()
    sysfiles.exposed=True

    def health(self):
        subcall = generator.health(notify=False)
        return subcall
    health.exposed=True

    def logfiles(self):
        subcall = subroutines()
        return subcall.syslogs_subroutine()
    logfiles.exposed=True

    def processes(self):
        subcall = subroutines()
        return subcall.sysprocesses_subroutine()
    processes.exposed=True

    def add_remove_logs(self, action=None, program=None, logpath=None):
        myDB = database.DBConnection()

        if action == 'addlog':
            if len(program) !=0 and len(logpath) !=0:
                controlValueDict = {"Program": program}
                newValueDict = {
                    "LogPath":   logpath
                    }
                myDB.upsert("logpaths", newValueDict, controlValueDict)
        elif action == 'removelog':
            myDB.select("DELETE from logpaths WHERE Program=?", [program])
        raise cherrypy.HTTPRedirect('home')
    add_remove_logs.exposed = True

    def add_remove_rules(self, action=None, id_num=None, rule1=None, rule2=None, rule3=None, rule4=None, rule5=None, rule6=None, rule7=None):
        myDB = database.DBConnection()

        if id_num is None:
            try:
                rule_id = myDB.select('SELECT id_num from rules')
                max_value = 0
            except:
                max_value = 0
            for ident in rule_id:
                test_value = ident['id_num']
                if test_value > max_value:
                    max_value = test_value
            id_num = max_value + 1

        if action == 'addrule':
            controlValueDict = {"id_num": id_num}
            newValueDict = {
                "rule1":   rule1,
                "rule2":   rule2,
                "rule3":   rule3,
                "rule4":   rule4,
                "rule5":   rule5,
                "rule6":   rule6,
                "rule7":   rule7,
                }
            myDB.upsert("rules", newValueDict, controlValueDict)
        if action == 'removerule':
            myDB.select("DELETE from rules WHERE id_num=?", [id_num])
        raise cherrypy.HTTPRedirect('home')
    add_remove_rules.exposed = True

    @cherrypy.expose
    def twitterStep1(self):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"

        return notifiers.twitter_notifier._get_authorization()

    @cherrypy.expose
    def twitterStep2(self, key):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"

        result = notifiers.twitter_notifier._get_credentials(key)
        logger.info(u"result: "+str(result))
        if result:
            return "Key verification successful"
        else:
            return "Unable to verify key"

    @cherrypy.expose
    def testTwitter(self):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"

        result = notifiers.twitter_notifier.test_notify()
        if result:
            return "Tweet successful, check your twitter to make sure it worked"
        else:
            return "Error sending tweet"
