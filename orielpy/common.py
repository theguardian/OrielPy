import os.path
import operator
import platform
import re

USER_AGENT = 'OrielPy' + ' (' + platform.system() + ' ' + platform.release() + ')'

### Notification Types
NOTIFY_PREPEND = 1

notifyStrings = {}
notifyStrings[NOTIFY_PREPEND] = ""
