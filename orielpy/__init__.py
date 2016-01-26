from cherrystrap import logger
from cherrystrap.configCheck import CheckSection, check_setting_int, check_setting_bool, check_setting_str

CPU_INFO_PATH = None
PSEUDOFILE_FOLDER = None
NUM_INTERNAL_DISK_CAPACITY = 0
SYS_FAN_FILE = None
SYS_FAN_MIN = 0
SYS_FAN_MAX = 0
CPU_FAN_FILE = None
CPU_FAN_MIN = 0
CPU_FAN_MAX = 0
CPU_TEMP_FILE = None
CPU_TEMP_MIN = 0
CPU_TEMP_MAX = 0
SYS_TEMP_FILE = None
SYS_TEMP_MIN = 0
SYS_TEMP_MAX = 0
NIC_READ_MAX = 0
NIC_WRITE_MAX = 0
INTERNAL_DISK_MAX_RATE = 0
EXTERNAL_DISK_MAX_RATE = 0

NOTIFICATION_TYPE = None
NOTIFICATION_FREQUENCY = 0
NOTIFICATION_UNITS = None
NOTIFICATION_CRON = None
NOTIFY_NOMINAL = False

TWITTER_ENABLED = False
TWITTER_TOKEN = None
TWITTER_SECRET = None
TWITTER_PREFIX = None

def injectVarCheck(CFG):

    global CPU_INFO_PATH, PSEUDOFILE_FOLDER, NUM_INTERNAL_DISK_CAPACITY, \
    SYS_FAN_FILE, SYS_FAN_MIN, SYS_FAN_MAX, CPU_FAN_FILE, CPU_FAN_MIN, \
    CPU_FAN_MAX, CPU_TEMP_FILE, CPU_TEMP_MIN, CPU_TEMP_MAX, SYS_TEMP_FILE, \
    SYS_TEMP_MIN, SYS_TEMP_MAX, NIC_READ_MAX, NIC_WRITE_MAX, \
    INTERNAL_DISK_MAX_RATE, EXTERNAL_DISK_MAX_RATE, \
    NOTIFICATION_TYPE, NOTIFICATION_FREQUENCY, NOTIFICATION_UNITS, \
    NOTIFICATION_CRON, NOTIFY_NOMINAL, \
    TWITTER_ENABLED, TWITTER_TOKEN, TWITTER_SECRET, TWITTER_PREFIX

    CheckSection(CFG, 'System')
    CheckSection(CFG, 'Notifications')

    CPU_INFO_PATH = check_setting_str(CFG, 'System', 'cpuInfoPath', '/proc/cpuinfo')
    PSEUDOFILE_FOLDER = check_setting_str(CFG, 'System', 'pseudofileFolder', '/sys/devices/virtual/thermal/thermal_zone0/')
    NUM_INTERNAL_DISK_CAPACITY = check_setting_int(CFG, 'System', 'numIntDiskCap', 1)
    SYS_FAN_FILE = check_setting_str(CFG, 'System', 'sysFanFile', '')
    SYS_FAN_MIN = check_setting_int(CFG, 'System', 'sysFanMin', 0)
    SYS_FAN_MAX = check_setting_int(CFG, 'System', 'sysFanMax', 5000)
    CPU_FAN_FILE = check_setting_str(CFG, 'System', 'cpuFanFile', '')
    CPU_FAN_MIN = check_setting_int(CFG, 'System', 'cpuFanMin', 0)
    CPU_FAN_MAX = check_setting_int(CFG, 'System', 'cpuFanMax', 5000)
    CPU_TEMP_FILE = check_setting_str(CFG, 'System', 'cpuTempFile', 'temp')
    CPU_TEMP_MIN = check_setting_int(CFG, 'System', 'cpuTempMin', 0)
    CPU_TEMP_MAX = check_setting_int(CFG, 'System', 'cpuTempMax', 100)
    SYS_TEMP_FILE = check_setting_str(CFG, 'System', 'sysTempFile', '')
    SYS_TEMP_MIN = check_setting_int(CFG, 'System', 'sysTempMin', 0)
    SYS_TEMP_MAX = check_setting_int(CFG, 'System', 'sysTempMax', 100)
    NIC_READ_MAX = check_setting_int(CFG, 'System', 'nicReadMax', 200)
    NIC_WRITE_MAX = check_setting_int(CFG, 'System', 'nicWriteMax', 200)
    INTERNAL_DISK_MAX_RATE = check_setting_int(CFG, 'System', 'intDiskMaxRate', 200)
    EXTERNAL_DISK_MAX_RATE = check_setting_int(CFG, 'System', 'extDiskMaxRate', 200)

    NOTIFICATION_TYPE = check_setting_str(CFG, 'Notifications', 'notificationType', 'disabled')
    NOTIFICATION_FREQUENCY = check_setting_int(CFG, 'Notifications', 'notificationFrequency', 0)
    NOTIFICATION_UNITS = check_setting_str(CFG, 'Notifications', 'notificationUnits', 'hours')
    NOTIFICATION_CRON = check_setting_str(CFG, 'Notifications', 'notificationCron', '0 5 * * 1')
    NOTIFY_NOMINAL = check_setting_bool(CFG, 'Notifications', 'notifyNominal', False)

    TWITTER_ENABLED = check_setting_bool(CFG, 'Notifications', 'twitterEnabled', False)
    TWITTER_TOKEN = check_setting_str(CFG, 'Notifications', 'twitterToken', '')
    TWITTER_SECRET = check_setting_str(CFG, 'Notifications', 'twitterSecret', '')
    TWITTER_PREFIX = check_setting_str(CFG, 'Notifications', 'twitterPrefix', 'OrielPy')

def injectDbSchema():

    schema = {}
    schema['logpaths'] = {} #this is a table name
    schema['logpaths']['Program'] = 'TEXT' #this is a column name and format
    schema['logpaths']['LogPath'] = 'TEXT'

    schema['rules'] = {}
    schema['rules']['rule1'] = 'TEXT'
    schema['rules']['rule2'] = 'TEXT'
    schema['rules']['rule3'] = 'TEXT'
    schema['rules']['rule4'] = 'TEXT'
    schema['rules']['rule5'] = 'TEXT'
    schema['rules']['rule6'] = 'TEXT'
    schema['rules']['rule7'] = 'TEXT'

    return schema

def injectApiConfigGet():

    injection = {
        "system": {
            "cpuInfoPath": CPU_INFO_PATH,
            "pseudofileFolder": PSEUDOFILE_FOLDER,
            "numIntDiskCap": NUM_INTERNAL_DISK_CAPACITY,
            "sysFanFile": SYS_FAN_FILE,
            "sysFanMin": SYS_FAN_MIN,
            "sysFanMax": SYS_FAN_MAX,
            "cpuFanFile": CPU_FAN_FILE,
            "cpuFanMin": CPU_FAN_MIN,
            "cpuFanMax": CPU_FAN_MAX,
            "cpuTempFile": CPU_TEMP_FILE,
            "cpuTempMin": CPU_TEMP_MIN,
            "cpuTempMax": CPU_TEMP_MAX,
            "sysTempFile": SYS_TEMP_FILE,
            "sysTempMin": SYS_TEMP_MIN,
            "sysTempMax": SYS_TEMP_MAX,
            "nicReadMax": NIC_READ_MAX,
            "nicWriteMax": NIC_WRITE_MAX,
            "intDiskMaxRate": INTERNAL_DISK_MAX_RATE,
            "extDiskMaxRate": EXTERNAL_DISK_MAX_RATE
        },
        "notifications": {
            "notificationType": NOTIFICATION_TYPE,
            "notificationFrequency": NOTIFICATION_FREQUENCY,
            "notificationUnits": NOTIFICATION_UNITS,
            "notificationCron": NOTIFICATION_CRON,
            "notifyNominal": NOTIFY_NOMINAL,
            "twitterEnabled": TWITTER_ENABLED,
            "twitterToken": TWITTER_TOKEN,
            "twitterSecret": TWITTER_SECRET,
            "twitterPrefix": TWITTER_PREFIX
        }
    }

    return injection

def injectApiConfigPut(kwargs, errorList):
    global CPU_INFO_PATH, PSEUDOFILE_FOLDER, NUM_INTERNAL_DISK_CAPACITY, \
    SYS_FAN_FILE, SYS_FAN_MIN, SYS_FAN_MAX, CPU_FAN_FILE, CPU_FAN_MIN, \
    CPU_FAN_MAX, CPU_TEMP_FILE, CPU_TEMP_MIN, CPU_TEMP_MAX, SYS_TEMP_FILE, \
    SYS_TEMP_MIN, SYS_TEMP_MAX, NIC_READ_MAX, NIC_WRITE_MAX, \
    INTERNAL_DISK_MAX_RATE, EXTERNAL_DISK_MAX_RATE, \
    NOTIFICATION_TYPE, NOTIFICATION_FREQUENCY, NOTIFICATION_UNITS, \
    NOTIFICATION_CRON, NOTIFY_NOMINAL, \
    TWITTER_ENABLED, TWITTER_TOKEN, TWITTER_SECRET, TWITTER_PREFIX

    if 'cpuInfoPath' in kwargs:
        CPU_INFO_PATH = kwargs.pop('cpuInfoPath', '/proc/cpuinfo')
    if 'pseudofileFolder' in kwargs:
        PSEUDOFILE_FOLDER = kwargs.pop('pseudofileFolder', '/sys/devices/virtual/thermal/thermal_zone0/')
    if 'numIntDiskCap' in kwargs:
        try:
            NUM_INTERNAL_DISK_CAPACITY = int(kwargs.pop('numIntDiskCap', 1))
        except:
            NUM_INTERNAL_DISK_CAPACITY = 1
            errorList.append("numIntDiskCap must be an integer")
            kwargs.pop('numIntDiskCap', 1)
    if 'sysFanFile' in kwargs:
        SYS_FAN_FILE = kwargs.pop('sysFanFile', '')
    if 'sysFanMin' in kwargs:
        try:
            SYS_FAN_MIN = int(kwargs.pop('sysFanMin', 0))
        except:
            SYS_FAN_MIN = 0
            errorList.append("sysFanMin must be an integer")
            kwargs.pop('sysFanMin', 0)
    if 'sysFanMax' in kwargs:
        try:
            SYS_FAN_MAX = int(kwargs.pop('sysFanMax', 5000))
        except:
            SYS_FAN_MAX = 5000
            errorList.append("sysFanMax must be an integer")
            kwargs.pop('sysFanMax', 5000)
    if 'cpuFanFile' in kwargs:
        CPU_FAN_FILE = kwargs.pop('cpuFanFile', None)
    if 'cpuFanMin' in kwargs:
        try:
            CPU_FAN_MIN = int(kwargs.pop('cpuFanMin', 0))
        except:
            CPU_FAN_MIN = 0
            errorList.append("cpuFanMin must be an integer")
            kwargs.pop('cpuFanMin', 0)
    if 'cpuFanMax' in kwargs:
        try:
            CPU_FAN_MAX = int(kwargs.pop('cpuFanMax', 5000))
        except:
            CPU_FAN_MAX = 5000
            errorList.append("cpuFanMax must be an integer")
            kwargs.pop('cpuFanMax', 5000)
    if 'cpuTempFile' in kwargs:
        CPU_TEMP_FILE = kwargs.pop('cpuTempFile', 'temp')
    if 'cpuTempMin' in kwargs:
        try:
            CPU_TEMP_MIN = int(kwargs.pop('cpuTempMin', 0))
        except:
            CPU_TEMP_MIN = 0
            errorList.append("cpuTempMin must be an integer")
            kwargs.pop('cpuTempMin', 0)
    if 'cpuTempMax' in kwargs:
        try:
            CPU_TEMP_MAX = int(kwargs.pop('cpuTempMax', 100))
        except:
            CPU_TEMP_MAX = 100
            errorList.append("cpuTempMax must be an integer")
            kwargs.pop('cpuTempMax', 100)
    if 'sysTempFile' in kwargs:
        SYS_TEMP_FILE = kwargs.pop('sysTempFile', None)
    if 'sysTempMin' in kwargs:
        try:
            SYS_TEMP_MIN = int(kwargs.pop('sysTempMin', 0))
        except:
            SYS_TEMP_MIN = 0
            errorList.append("sysTempMin must be an integer")
            kwargs.pop('sysTempMin', 0)
    if 'sysTempMax' in kwargs:
        try:
            SYS_TEMP_MAX = int(kwargs.pop('sysTempMax', 100))
        except:
            SYS_TEMP_MAX = 100
            errorList.append("sysTempMax must be an integer")
            kwargs.pop('sysTempMax', 100)
    if 'nicReadMax' in kwargs:
        try:
            NIC_READ_MAX = int(kwargs.pop('nicReadMax', 200))
        except:
            NIC_READ_MAX = 200
            errorList.append("nicReadMax must be an integer")
            kwargs.pop('nicReadMax', 200)
    if 'nicWriteMax' in kwargs:
        try:
            NIC_WRITE_MAX = int(kwargs.pop('nicWriteMax', 200))
        except:
            NIC_WRITE_MAX = 200
            errorList.append("nicWriteMax must be an integer")
            kwargs.pop('nicWriteMax', 0)
    if 'intDiskMaxRate' in kwargs:
        try:
            INTERNAL_DISK_MAX_RATE = int(kwargs.pop('intDiskMaxRate', 200))
        except:
            INTERNAL_DISK_MAX_RATE = 200
            errorList.append("intDiskMaxRate must be an integer")
            kwargs.pop('intDiskMaxRate', 200)
    if 'extDiskMaxRate' in kwargs:
        try:
            EXTERNAL_DISK_MAX_RATE = int(kwargs.pop('extDiskMaxRate', 200))
        except:
            EXTERNAL_DISK_MAX_RATE = 200
            errorList.append("extDiskMaxRate must be an integer")
            kwargs.pop('extDiskMaxRate', 200)
    if 'notificationType' in kwargs:
        NOTIFICATION_TYPE = kwargs.pop('notificationType', 'disabled')
    if 'notificationFrequency' in kwargs:
        try:
            NOTIFICATION_FREQUENCY = int(kwargs.pop('notificationFrequency', 0))
        except:
            NOTIFICATION_FREQUENCY = 0
            errorList.append("notificationFrequency must be an integer")
            kwargs.pop('notificationFrequency', 0)
    if 'notificationUnits' in kwargs:
        NOTIFICATION_UNITS = kwargs.pop('notificationUnits', 'hours')
    if 'notificationCron' in kwargs:
        NOTIFICATION_CRON = kwargs.pop('notificationCron', '0 5 * * 1')
    if 'notifyNominal' in kwargs:
        NOTIFY_NOMINAL = kwargs.pop('notifyNominal', False) == 'true'
    elif 'notifyNominalHidden' in kwargs:
        NOTIFY_NOMINAL = kwargs.pop('notifyNominalHidden', False) == 'true'
    if 'twitterEnabled' in kwargs:
        TWITTER_ENABLED = kwargs.pop('twitterEnabled', False) == 'true'
    elif 'twitterEnabledHidden' in kwargs:
        TWITTER_ENABLED = kwargs.pop('twitterEnabledHidden', False) == 'true'
    if 'twitter_key' in kwargs:
        kwargs.pop('twitter_key', '')
    if 'twitterToken' in kwargs:
        TWITTER_TOKEN = kwargs.pop('twitterToken', '')
    if 'twitterSecret' in kwargs:
        TWITTER_SECRET = kwargs.pop('twitterSecret', '')
    if 'twitterPrefix' in kwargs:
        TWITTER_PREFIX = kwargs.pop('twitterPrefix', 'OrielPy')

    return kwargs, errorList

def injectVarWrite(new_config):
    new_config['System'] = {}
    new_config['System']['cpuInfoPath'] = CPU_INFO_PATH
    new_config['System']['pseudofileFolder'] = PSEUDOFILE_FOLDER
    new_config['System']['numIntDiskCap'] = NUM_INTERNAL_DISK_CAPACITY
    new_config['System']['sysFanFile'] = SYS_FAN_FILE
    new_config['System']['sysFanMin'] = SYS_FAN_MIN
    new_config['System']['sysFanMax'] = SYS_FAN_MAX
    new_config['System']['cpuFanFile'] = CPU_FAN_FILE
    new_config['System']['cpuFanMin'] = CPU_FAN_MIN
    new_config['System']['cpuFanMax'] = CPU_FAN_MAX
    new_config['System']['cpuTempFile'] = CPU_TEMP_FILE
    new_config['System']['cpuTempMin'] = CPU_TEMP_MIN
    new_config['System']['cpuTempMax'] = CPU_TEMP_MAX
    new_config['System']['sysTempFile'] = SYS_TEMP_FILE
    new_config['System']['sysTempMin'] = SYS_TEMP_MIN
    new_config['System']['sysTempMax'] = SYS_TEMP_MAX
    new_config['System']['nicReadMax'] = NIC_READ_MAX
    new_config['System']['nicWriteMax'] = NIC_WRITE_MAX
    new_config['System']['intDiskMaxRate'] = INTERNAL_DISK_MAX_RATE
    new_config['System']['extDiskMaxRate'] = EXTERNAL_DISK_MAX_RATE

    new_config['Notifications'] = {}
    new_config['Notifications']['notificationType'] = NOTIFICATION_TYPE
    new_config['Notifications']['notificationFrequency'] = NOTIFICATION_FREQUENCY
    new_config['Notifications']['notificationUnits'] = NOTIFICATION_UNITS
    new_config['Notifications']['notificationCron'] = NOTIFICATION_CRON
    new_config['Notifications']['notifyNominal'] = NOTIFY_NOMINAL
    new_config['Notifications']['twitterEnabled'] = TWITTER_ENABLED
    new_config['Notifications']['twitterToken'] = TWITTER_TOKEN
    new_config['Notifications']['twitterSecret'] = TWITTER_SECRET
    new_config['Notifications']['twitterPrefix'] = TWITTER_PREFIX

    return new_config
