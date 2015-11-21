from __future__ import with_statement

import os, sys, subprocess, threading, cherrypy, sqlite3

import datetime

from lib.configobj import ConfigObj
from lib.apscheduler.scheduler import Scheduler

import threading

from orielpy import logger, generator

FULL_PATH = None
PROG_DIR = None

ARGS = None
SIGNAL = None

LOGLEVEL = 1
DAEMON = False
PIDFILE = None

SYS_ENCODING = None

SCHED = Scheduler()

INIT_LOCK = threading.Lock()
__INITIALIZED__ = False
started = False

DATADIR = None
DBFILE=None
CONFIGFILE = None
CFG = None

LOGDIR = None
LOGLIST = []

SERVER_NAME = None
HTTP_HOST = None
HTTP_PORT = None
HTTP_USER = None
HTTP_PASS = None
HTTP_ROOT = None
HTTP_LOOK = None
VERIFY_SSL = None
LAUNCH_BROWSER = False
NOTIFICATION_FREQUENCY = 0
NOTIFICATION_UNITS = None
NOTIFY_NOMINAL = False

CPU_INFO_PATH = None
PSEUDOFILE_FOLDER = None
NUM_INTERNAL_DISK_CAPACITY = None
SYS_FAN_FILE = None
SYS_FAN_MIN = None
SYS_FAN_MAX = None
CPU_FAN_FILE = None
CPU_FAN_MIN = None
CPU_FAN_MAX = None
CPU_TEMP_FILE = None
CPU_TEMP_MIN = None
CPU_TEMP_MAX = None
SYS_TEMP_FILE = None
SYS_TEMP_MIN = None
SYS_TEMP_MAX = None
NIC_READ_MAX = None
NIC_WRITE_MAX = None
INTERNAL_DISK_MAX_RATE = None
EXTERNAL_DISK_MAX_RATE = None

USE_TWITTER = False
TWITTER_USERNAME = None
TWITTER_PASSWORD = None
TWITTER_PREFIX = 'OrielPy'


def CheckSection(sec):
    """ Check if INI section exists, if not create it """
    try:
        CFG[sec]
        return True
    except:
        CFG[sec] = {}
        return False

#################################################################################
## Check_setting_int                                                            #
#################################################################################
#def minimax(val, low, high):
#    """ Return value forced within range """
#    try:
#        val = int(val)
#    except:
#        val = 0
#    if val < low:
#        return low
#    if val > high:
#        return high
#    return val

################################################################################
# Check_setting_int                                                            #
################################################################################
def check_setting_int(config, cfg_name, item_name, def_val):
    try:
        my_val = int(config[cfg_name][item_name])
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val
    logger.debug(item_name + " -> " + str(my_val))
    return my_val

#################################################################################
## Check_setting_float                                                          #
#################################################################################
##def check_setting_float(config, cfg_name, item_name, def_val):
##    try:
##        my_val = float(config[cfg_name][item_name])
##    except:
##        my_val = def_val
##        try:
##            config[cfg_name][item_name] = my_val
##        except:
##            config[cfg_name] = {}
##            config[cfg_name][item_name] = my_val

##    return my_val

################################################################################
# Check_setting_str                                                            #
################################################################################
def check_setting_str(config, cfg_name, item_name, def_val, log=True):
    try:
        my_val = config[cfg_name][item_name]
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val

    if log:
        logger.debug(item_name + " -> " + my_val)
    else:
        logger.debug(item_name + " -> ******")

    return my_val

def initialize():

    with INIT_LOCK:

        global __INITIALIZED__, FULL_PATH, PROG_DIR, LOGLEVEL, DAEMON, DATADIR, CONFIGFILE, CFG, LOGDIR, SERVER_NAME, HTTP_HOST, HTTP_PORT, HTTP_USER, HTTP_PASS, HTTP_ROOT, HTTP_LOOK, \
        VERIFY_SSL, LAUNCH_BROWSER, \
        NOTIFY_NOMINAL, CPU_INFO_PATH, PSEUDOFILE_FOLDER, NUM_INTERNAL_DISK_CAPACITY, SYS_FAN_FILE, SYS_FAN_MIN, SYS_FAN_MAX, CPU_FAN_FILE, CPU_FAN_MIN, CPU_FAN_MAX, \
        CPU_TEMP_FILE, CPU_TEMP_MIN, CPU_TEMP_MAX, SYS_TEMP_FILE, SYS_TEMP_MIN, SYS_TEMP_MAX, NIC_READ_MAX, NIC_WRITE_MAX, INTERNAL_DISK_MAX_RATE, \
        EXTERNAL_DISK_MAX_RATE, USE_TWITTER, TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_PREFIX, NOTIFICATION_FREQUENCY, NOTIFICATION_UNITS

        if __INITIALIZED__:
            return False

        CheckSection('General')
        CheckSection('Server')
        CheckSection('Twitter')

        try:
            HTTP_PORT = check_setting_int(CFG, 'General', 'http_port', 5151)
        except:
            HTTP_PORT = 5151

        if HTTP_PORT < 21 or HTTP_PORT > 65535:
            HTTP_PORT = 5151

        SERVER_NAME = check_setting_str(CFG, 'General', 'server_name', 'Server')
        HTTP_HOST = check_setting_str(CFG, 'General', 'http_host', '0.0.0.0')
        HTTP_USER = check_setting_str(CFG, 'General', 'http_user', '')
        HTTP_PASS = check_setting_str(CFG, 'General', 'http_pass', '')
        HTTP_ROOT = check_setting_str(CFG, 'General', 'http_root', '')
        HTTP_LOOK = check_setting_str(CFG, 'General', 'http_look', 'default')
        VERIFY_SSL = bool(check_setting_int(CFG, 'General', 'verify_ssl', 1))
        LAUNCH_BROWSER = bool(check_setting_int(CFG, 'General', 'launch_browser', 0))
        LOGDIR = check_setting_str(CFG, 'General', 'logdir', '')
        NOTIFICATION_FREQUENCY = int(check_setting_int(CFG, 'General', 'notification_frequency', 0))
        NOTIFICATION_UNITS = check_setting_str(CFG, 'General', 'notification_units', '')
        NOTIFY_NOMINAL = bool(check_setting_int(CFG, 'General', 'notify_nominal', 0))

        CPU_INFO_PATH = check_setting_str(CFG, 'Server', 'cpu_info_path', '/proc/cpuinfo')
        PSEUDOFILE_FOLDER = check_setting_str(CFG, 'Server', 'pseudofile_folder', '/sys/devices/virtual/thermal/thermal_zone0/')
        NUM_INTERNAL_DISK_CAPACITY = int(check_setting_str(CFG, 'Server', 'num_internal_disk_capacity', '0'))
        SYS_FAN_FILE = check_setting_str(CFG, 'Server', 'sys_fan_file', '')
        SYS_FAN_MIN = int(check_setting_str(CFG, 'Server', 'sys_fan_min', '0'))
        SYS_FAN_MAX = int(check_setting_str(CFG, 'Server', 'sys_fan_max', '5000'))
        CPU_FAN_FILE = check_setting_str(CFG, 'Server', 'cpu_fan_file', '')
        CPU_FAN_MIN = int(check_setting_str(CFG, 'Server', 'cpu_fan_min', '0'))
        CPU_FAN_MAX = int(check_setting_str(CFG, 'Server', 'cpu_fan_max', '5000'))
        CPU_TEMP_FILE = check_setting_str(CFG, 'Server', 'cpu_temp_file', 'temp')
        CPU_TEMP_MIN = int(check_setting_str(CFG, 'Server', 'cpu_temp_min', '0'))
        CPU_TEMP_MAX = int(check_setting_str(CFG, 'Server', 'cpu_temp_max', '100'))
        SYS_TEMP_FILE = check_setting_str(CFG, 'Server', 'sys_temp_file', '')
        SYS_TEMP_MIN = int(check_setting_str(CFG, 'Server', 'sys_temp_min', '0'))
        SYS_TEMP_MAX = int(check_setting_str(CFG, 'Server', 'sys_temp_max', '100'))
        NIC_READ_MAX = int(check_setting_str(CFG, 'Server', 'nic_read_max', '200'))
        NIC_WRITE_MAX = int(check_setting_str(CFG, 'Server', 'nic_write_max', '200'))
        INTERNAL_DISK_MAX_RATE = int(check_setting_str(CFG, 'Server', 'internal_disk_max_rate', '200'))
        EXTERNAL_DISK_MAX_RATE = int(check_setting_str(CFG, 'Server', 'external_disk_max_rate', '200'))

        USE_TWITTER = bool(check_setting_int(CFG, 'Twitter', 'use_twitter', 0))
        TWITTER_USERNAME = check_setting_str(CFG, 'Twitter', 'twitter_username', '')
        TWITTER_PASSWORD = check_setting_str(CFG, 'Twitter', 'twitter_password', '')
        TWITTER_PREFIX = check_setting_str(CFG, 'Twitter', 'twitter_prefix', 'OrielPy')


        if not LOGDIR:
            LOGDIR = os.path.join(DATADIR, 'Logs')

        # Put the cache dir in the data dir for now
        CACHEDIR = os.path.join(DATADIR, 'cache')
        if not os.path.exists(CACHEDIR):
            try:
                os.makedirs(CACHEDIR)
            except OSError:
                logger.error('Could not create cachedir. Check permissions of: ' + DATADIR)

        # Create logdir
        if not os.path.exists(LOGDIR):
            try:
                os.makedirs(LOGDIR)
            except OSError:
                if LOGLEVEL:
                    print LOGDIR + ":"
                    print ' Unable to create folder for logs. Only logging to console.'

        # Start the logger, silence console logging if we need to
        logger.orielpy_log.initLogger(loglevel=LOGLEVEL)

        # Initialize the database
        try:
            dbcheck()
        except Exception, e:
            logger.error("Can't connect to the database: %s" % e)

        __INITIALIZED__ = True
        return True

def daemonize():
    """
    Fork off as a daemon
    """

    # Make a non-session-leader child process
    try:
        pid = os.fork() #@UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" %
                   (e.strerror, e.errno))

    os.setsid() #@UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork() #@UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("2st fork failed: %s [%d]" %
                   (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())

    if PIDFILE:
        pid = str(os.getpid())
        logger.debug(u"Writing PID " + pid + " to " + str(PIDFILE))
        file(PIDFILE, 'w').write("%s\n" % pid)

def launch_browser(host, port, root):
    if host == '0.0.0.0':
        host = 'localhost'

    try:
        import webbrowser
        webbrowser.open('http://%s:%i%s' % (host, port, root))
    except Exception, e:
        logger.error('Could not launch browser: %s' % e)

def config_write():
    new_config = ConfigObj()
    new_config.filename = CONFIGFILE

    new_config['General'] = {}
    new_config['General']['server_name'] = SERVER_NAME
    new_config['General']['http_port'] = HTTP_PORT
    new_config['General']['http_host'] = HTTP_HOST
    new_config['General']['http_user'] = HTTP_USER
    new_config['General']['http_pass'] = HTTP_PASS
    new_config['General']['http_root'] = HTTP_ROOT
    new_config['General']['http_look'] = HTTP_LOOK
    new_config['General']['verify_ssl'] = int(VERIFY_SSL)
    new_config['General']['launch_browser'] = int(LAUNCH_BROWSER)
    new_config['General']['logdir'] = LOGDIR
    new_config['General']['notification_frequency'] = int(NOTIFICATION_FREQUENCY)
    new_config['General']['notification_units'] = NOTIFICATION_UNITS
    new_config['General']['notify_nominal'] = int(NOTIFY_NOMINAL)

    new_config['Server'] = {}
    new_config['Server']['cpu_info_path'] = CPU_INFO_PATH
    new_config['Server']['pseudofile_folder'] = PSEUDOFILE_FOLDER
    new_config['Server']['num_internal_disk_capacity'] = int(NUM_INTERNAL_DISK_CAPACITY)
    new_config['Server']['sys_fan_file'] = SYS_FAN_FILE
    new_config['Server']['sys_fan_min'] = int(SYS_FAN_MIN)
    new_config['Server']['sys_fan_max'] = int(SYS_FAN_MAX)
    new_config['Server']['cpu_fan_file'] = CPU_FAN_FILE
    new_config['Server']['cpu_fan_min'] = int(CPU_FAN_MIN)
    new_config['Server']['cpu_fan_max'] = int(CPU_FAN_MAX)
    new_config['Server']['cpu_temp_file'] = CPU_TEMP_FILE
    new_config['Server']['cpu_temp_min'] = int(CPU_TEMP_MIN)
    new_config['Server']['cpu_temp_max'] = int(CPU_TEMP_MAX)
    new_config['Server']['sys_temp_file'] = SYS_TEMP_FILE
    new_config['Server']['sys_temp_min'] = int(SYS_TEMP_MIN)
    new_config['Server']['sys_temp_max'] = int(SYS_TEMP_MAX)
    new_config['Server']['nic_read_max'] = int(NIC_READ_MAX)
    new_config['Server']['nic_write_max'] = int(NIC_WRITE_MAX)
    new_config['Server']['internal_disk_max_rate'] = int(INTERNAL_DISK_MAX_RATE)
    new_config['Server']['external_disk_max_rate'] = int(EXTERNAL_DISK_MAX_RATE)

    new_config['Twitter'] = {}
    new_config['Twitter']['use_twitter'] = int(USE_TWITTER)
    new_config['Twitter']['twitter_username'] = TWITTER_USERNAME
    new_config['Twitter']['twitter_password'] = TWITTER_PASSWORD
    new_config['Twitter']['twitter_prefix'] = TWITTER_PREFIX

    new_config.write()

def dbcheck():

    conn=sqlite3.connect(DBFILE)
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logpaths (Program TEXT, LogPath TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rules (id_num INTEGER, rule1 TEXT, rule2 TEXT, rule3 TEXT, rule4 TEXT, rule5 TEXT, rule6 TEXT, rule7 TEXT)')

    conn.commit()
    c.close()

def start():
    global __INITIALIZED__, started

    if __INITIALIZED__:

        # Crons and scheduled jobs go here
        starttime = datetime.datetime.now()
        if NOTIFICATION_UNITS == "hours" and NOTIFICATION_FREQUENCY != 0:
            SCHED.add_interval_job(generator.health, hours=NOTIFICATION_FREQUENCY)
        elif NOTIFICATION_UNITS == "minutes" and NOTIFICATION_FREQUENCY !=0:
            SCHED.add_interval_job(generator.health, minutes=NOTIFICATION_FREQUENCY)
        #SCHED.add_interval_job(searchnzb.searchbook, minutes=SEARCH_INTERVAL, start_date=starttime+datetime.timedelta(minutes=2))

        SCHED.start()
#        for job in SCHED.get_jobs():
#            print job
        started = True

def shutdown(restart=False):
    config_write()
    logger.info('orielpy is shutting down ...')
    cherrypy.engine.exit()

    SCHED.shutdown(wait=True)

    if PIDFILE :
        logger.info('Removing pidfile %s' % PIDFILE)
        os.remove(PIDFILE)

    if restart:
        logger.info('orielpy is restarting ...')
        popen_list = [sys.executable, FULL_PATH]
        popen_list += ARGS
        if '--nolaunch' not in popen_list:
            popen_list += ['--nolaunch']
            logger.info('Restarting orielpy with ' + str(popen_list))
        subprocess.Popen(popen_list, cwd=os.getcwd())

    os._exit(0)
