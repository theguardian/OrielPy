import os, cherrypy, urllib, collections
from cherrypy import _cperror
from cherrypy.lib.static import serve_file
import simplejson as json
from cherrystrap.auth import AuthController, require, member_of, name_is
from cherrystrap.templating import serve_template

import threading, time

import cherrystrap

from cherrystrap import logger, formatter
from orielpy.subroutines import subroutines
from orielpy.notifiers import twitter_notifier

SESSION_KEY = '_cp_username'

class WebInterface(object):

    def error_page_404(status, message, traceback, version):
        status_msg = "%s - %s" % (status, message)
        return serve_template(templatename="index.html", title="404 - Page Not Found", msg=status_msg)
    cherrypy.config.update({'error_page.404': error_page_404})

    def handle_error():
        cherrypy.response.status = 500
        logger.error("500 Error: %s" % _cperror.format_exc())
        cherrypy.response.body = ["<html><body>Sorry, an error occured</body></html>"]

    _cp_config = {
        'tools.sessions.on': True,
        'tools.sessions.timeout': 10080,
        'tools.auth.on': True,
        'error_page.404': error_page_404,
        'request.error_response': handle_error
    }

    auth = AuthController()

    @require()
    def index(self):
        subroutine = subroutines()
        staticData = subroutine.static_subroutine()
        numCPUs = len(subroutine.cpuload_subroutine())
        numDisks = len(subroutine.diskio_subroutine())
        numPartitions = len(subroutine.partitions_subroutine())
        fansTemps = subroutine.sysfiles_subroutine()

        return serve_template(templatename="index.html", title="Home", staticData=staticData, numCPUs=numCPUs, numDisks=numDisks, numPartitions=numPartitions, fansTemps=fansTemps)
    index.exposed=True

    @require()
    def config(self):
        http_look_dir = os.path.join(cherrystrap.PROG_DIR, 'static/interfaces/')
        http_look_list = [ name for name in os.listdir(http_look_dir) if os.path.isdir(os.path.join(http_look_dir, name)) ]

        config = {
            "http_look_list":   http_look_list
        }

        return serve_template(templatename="config.html", title="Settings", config=config)
    config.exposed = True

    @require()
    def log(self):
        return serve_template(templatename="log.html", title="Log", lineList=cherrystrap.LOGLIST)
    log.exposed = True

    @require()
    def logs(self):
        return serve_template(templatename="logs.html", title="Logs")
    logs.exposed = True

    @require()
    def processes(self):
        return serve_template(templatename="processes.html", title="Processes")
    processes.exposed = True

    @require()
    def configlogs(self):
        return serve_template(templatename="configlogs.html", title="Configure Logs")
    configlogs.exposed = True

    @require()
    def configrules(self):
        return serve_template(templatename="configrules.html", title="Configure Rules")
    configrules.exposed = True

    def downloadLog(self, logFile=None):
        message = {}
        if logFile:
            try:
                return serve_file(logFile, "application/x-download", "attachment")
            except Exception as e:
                message['status'] = 'danger'
                message['message'] = 'There was a problem downloading log file %s' % logFile
                logger.error('There was a problem downloading log file %s: %s' % (logFile, e))
                return serve_template(templatename="logs.html", title="Logs", message=message)

        else:
            message['status'] = 'warning'
            message['message'] = 'You must define a logFile to download'
            return serve_template(templatename="logs.html", title="Logs", message=message)

    downloadLog.exposed = True

    @require()
    def shutdown(self):
        cherrystrap.config_write()
        cherrystrap.SIGNAL = 'shutdown'
        message = 'shutting down ...'
        return serve_template(templatename="shutdown.html", title="Exit", message=message, timer=10)
        return page
    shutdown.exposed = True

    @require()
    def restart(self):
        cherrystrap.SIGNAL = 'restart'
        message = 'restarting ...'
        return serve_template(templatename="shutdown.html", title="Restart", message=message, timer=15)
    restart.exposed = True

    @require()
    def shutdown(self):
        cherrystrap.config_write()
        cherrystrap.SIGNAL = 'shutdown'
        message = 'shutting down ...'
        return serve_template(templatename="shutdown.html", title="Exit", message=message, timer=15)
        return page
    shutdown.exposed = True

    @require()
    def update(self):
        cherrystrap.SIGNAL = 'update'
        message = 'updating ...'
        return serve_template(templatename="shutdown.html", title="Update", message=message, timer=30)
    update.exposed = True

    # Safe to delete this def, it's just there as a reference
    def template(self):
        return serve_template(templatename="template.html", title="Template Reference")
    template.exposed=True

    def checkGithub(self):
        # Make sure this is requested via ajax
        request_type = cherrypy.request.headers.get('X-Requested-With')
        if str(request_type).lower() == 'xmlhttprequest':
            pass
        else:
            status_msg = "This page exists, but is not accessible via web browser"
            return serve_template(templatename="index.html", title="404 - Page Not Found", msg=status_msg)

        from cherrystrap import versioncheck
        versioncheck.checkGithub()
        cherrystrap.IGNORE_UPDATES = False
    checkGithub.exposed = True

    def ignoreUpdates(self):
        # Make sure this is requested via ajax
        request_type = cherrypy.request.headers.get('X-Requested-With')
        if str(request_type).lower() == 'xmlhttprequest':
            pass
        else:
            status_msg = "This page exists, but is not accessible via web browser"
            return serve_template(templatename="index.html", title="404 - Page Not Found", msg=status_msg)

        cherrystrap.IGNORE_UPDATES = True
    ignoreUpdates.exposed = True

    def ajaxUpdate(self):
        # Make sure this is requested via ajax
        request_type = cherrypy.request.headers.get('X-Requested-With')
        if str(request_type).lower() == 'xmlhttprequest':
            pass
        else:
            status_msg = "This page exists, but is not accessible via web browser"
            return serve_template(templatename="index.html", title="404 - Page Not Found", msg=status_msg)

        return serve_template(templatename="ajaxUpdate.html")
    ajaxUpdate.exposed = True


    def twitterStep1(self):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"

        return twitter_notifier._get_authorization()
    twitterStep1.exposed = True

    def twitterStep2(self, key):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"
        message={}

        result = twitter_notifier._get_credentials(key)
        logger.info(u"result: "+str(result))

        if result:
            message['status'] = 'success'
            message['message'] = 'Key verification successful'
            return "Key verification successful"
        else:
            message['status'] = 'danger'
            message['message'] = 'Unable to verify key'
            return "Unable to verify key"
    twitterStep2.exposed = True

    def testTwitter(self):
        cherrypy.response.headers['Cache-Control'] = "max-age=0,no-cache,no-store"

        result = twitter_notifier.test_notify()
        if result:
            return "Tweet successful, check your twitter to make sure it worked"
        else:
            return "Error sending tweet"
    testTwitter.exposed = True
