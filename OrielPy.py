import os, sys, time, cherrypy, threading, locale
from lib.configobj import ConfigObj

import orielpy
from orielpy import webStart, logger

def main():

    # rename this thread
    threading.currentThread().name = "MAIN"

    # Set paths
    if hasattr(sys, 'frozen'):
        orielpy.FULL_PATH = os.path.abspath(sys.executable)
    else:
        orielpy.FULL_PATH = os.path.abspath(__file__)

    orielpy.PROG_DIR = os.path.dirname(orielpy.FULL_PATH)
    orielpy.ARGS = sys.argv[1:]

    orielpy.SYS_ENCODING = None

    try:
        locale.setlocale(locale.LC_ALL, "")
        orielpy.SYS_ENCODING = locale.getpreferredencoding()
    except (locale.Error, IOError):
        pass

    # for OSes that are poorly configured I'll just force UTF-8
    if not orielpy.SYS_ENCODING or orielpy.SYS_ENCODING in ('ANSI_X3.4-1968', 'US-ASCII', 'ASCII'):
        orielpy.SYS_ENCODING = 'UTF-8'

    # Set arguments
    from optparse import OptionParser

    p = OptionParser()
    p.add_option('-d', '--daemon', action = "store_true",
                 dest = 'daemon', help = "Run the server as a daemon")
    p.add_option('-q', '--quiet', action = "store_true",
                 dest = 'quiet', help = "Don't log to console")
    p.add_option('--debug', action="store_true",
                 dest = 'debug', help = "Show debuglog messages")
    p.add_option('--nolaunch', action = "store_true",
                 dest = 'nolaunch', help="Don't start browser")
    p.add_option('--port',
                 dest = 'port', default = None,
                 help = "Force webinterface to listen on this port")
    p.add_option('--datadir',
                 dest = 'datadir', default = None,
                 help = "Path to the data directory")
    p.add_option('--config',
                 dest = 'config', default = None,
                 help = "Path to config.ini file")
    p.add_option('-p', '--pidfile',
                 dest = 'pidfile', default = None,
                 help = "Store the process id in the given file")

    options, args = p.parse_args()

    if options.debug:
        orielpy.LOGLEVEL = 2

    if options.quiet:
        orielpy.LOGLEVEL = 0

    if options.daemon:
        if not sys.platform == 'win32':
            orielpy.DAEMON = True
            orielpy.LOGLEVEL = 0
            orielpy.daemonize()
        else:
            print "Daemonize not supported under Windows, starting normally"

    if options.nolaunch:
        orielpy.LAUNCH_BROWSER = False

    if options.datadir:
        orielpy.DATADIR = str(options.datadir)
    else:
        orielpy.DATADIR = orielpy.PROG_DIR

    if options.config:
        orielpy.CONFIGFILE = str(options.config)
    else:
        orielpy.CONFIGFILE = os.path.join(orielpy.DATADIR, "config.ini")

    if options.pidfile:
        if orielpy.DAEMON:
            orielpy.PIDFILE = str(options.pidfile)

    # create and check (optional) paths
    if not os.path.exists(orielpy.DATADIR):
        try:
            os.makedirs(orielpy.DATADIR)
        except OSError:
            raise SystemExit('Could not create data directory: ' + orielpy.DATADIR + '. Exit ...')

    if not os.access(orielpy.DATADIR, os.W_OK):
        raise SystemExit('Cannot write to the data directory: ' + orielpy.DATADIR + '. Exit ...')

    # create database and config
    orielpy.DBFILE = os.path.join(orielpy.DATADIR, 'orielpy.db')
    orielpy.CFG = ConfigObj(orielpy.CONFIGFILE, encoding='utf-8')

    orielpy.initialize()

    if options.port:
        HTTP_PORT = int(options.port)
        logger.info('Starting orielpy on forced port: %s' % HTTP_PORT)
    else:
        HTTP_PORT = int(orielpy.HTTP_PORT)
        logger.info('Starting orielpy on port: %s' % orielpy.HTTP_PORT)

    if orielpy.DAEMON:
        orielpy.daemonize()

    # Try to start the server. 
    webStart.initialize({
                    'http_port': HTTP_PORT,
                    'http_host': orielpy.HTTP_HOST,
                    'http_root': orielpy.HTTP_ROOT,
                    'http_user': orielpy.HTTP_USER,
                    'http_pass': orielpy.HTTP_PASS,
            })

    if orielpy.LAUNCH_BROWSER and not options.nolaunch:
        orielpy.launch_browser(orielpy.HTTP_HOST, orielpy.HTTP_PORT, orielpy.HTTP_ROOT)

    orielpy.start()

    while True:
        if not orielpy.SIGNAL:

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                orielpy.shutdown()
        else:
            if orielpy.SIGNAL == 'shutdown':
                orielpy.shutdown()
            elif orielpy.SIGNAL == 'restart':
                orielpy.shutdown(restart=True)
            else:
                orielpy.shutdown(restart=True, update=True)
            orielpy.SIGNAL = None
    return

if __name__ == "__main__":
    main()
