import orielpy
import tweet
from orielpy.common import *

twitter_notifier = tweet.TwitterNotifier()

notifiers = [
    twitter_notifier,
]

def notify_health(output):
    for n in notifiers:
        n.notify_health(output)
