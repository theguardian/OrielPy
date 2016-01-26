import cherrystrap
import orielpy

from cherrystrap import logger, formatter
from orielpy import common

# parse_qsl moved to urlparse module in v2.6
try:
    from urlparse import parse_qsl #@UnusedImport
except:
    from cgi import parse_qsl #@Reimport

import lib.oauth2 as oauth
import lib.pythontwitter as twitter

class TwitterNotifier:

    consumer_key = "ZUJt6TLfdoDx5MBZLCOFKQ"
    consumer_secret = "9gS5c4AAdhk6YSkL5F4E67Xclyao6GRDnXQKWCAw"

    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'


    def notify_health(self, output):
        self._notifyTwitter('OrielPy: '+common.notifyStrings[common.NOTIFY_PREPEND]+output)

    def test_notify(self):
        return self._notifyTwitter("This is a test notification from OrielPy / " + formatter.now(), force=True)

    def _get_authorization(self):

        signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1() #@UnusedVariable
        oauth_consumer             = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        oauth_client               = oauth.Client(oauth_consumer)

        logger.info('Requesting temp token from Twitter')

        resp, content = oauth_client.request(self.REQUEST_TOKEN_URL, 'GET')

        if resp['status'] != '200':
            logger.info('Invalid respond from Twitter requesting temp token: %s' % resp['status'])
        else:
            request_token = dict(parse_qsl(content))

            orielpy.TWITTER_TOKEN = request_token['oauth_token']
            orielpy.TWITTER_SECRET = request_token['oauth_token_secret']

            return self.AUTHORIZATION_URL+"?oauth_token="+ request_token['oauth_token']

    def _get_credentials(self, key):
        request_token = {}

        request_token['oauth_token'] = orielpy.TWITTER_TOKEN
        request_token['oauth_token_secret'] = orielpy.TWITTER_SECRET
        request_token['oauth_callback_confirmed'] = 'true'

        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(key)

        logger.info('Generating and signing request for an access token using key '+key)

        signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1() #@UnusedVariable
        oauth_consumer             = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        logger.info('oauth_consumer: '+str(oauth_consumer))
        oauth_client  = oauth.Client(oauth_consumer, token)
        logger.info('oauth_client: '+str(oauth_client))
        resp, content = oauth_client.request(self.ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % key)
        logger.info('resp, content: '+str(resp)+','+str(content))

        access_token  = dict(parse_qsl(content))
        logger.info('access_token: '+str(access_token))

        logger.info('resp[status] = '+str(resp['status']))
        if resp['status'] != '200':
            logger.error('The request for a token with did not succeed: '+str(resp['status']))
            return False
        else:
            logger.info('Your Twitter Access Token key: %s' % access_token['oauth_token'])
            logger.info('Access Token secret: %s' % access_token['oauth_token_secret'])
            orielpy.TWITTER_TOKEN = access_token['oauth_token']
            orielpy.TWITTER_SECRET = access_token['oauth_token_secret']
            return True


    def _send_tweet(self, message=None):

        username=self.consumer_key
        password=self.consumer_secret
        access_token_key=orielpy.TWITTER_TOKEN
        access_token_secret=orielpy.TWITTER_SECRET

        logger.info(u"Sending tweet: "+message)

        api = twitter.Api(username, password, access_token_key, access_token_secret)

        try:
            api.PostUpdate(message)
        except Exception, e:
            logger.error(u"Error Sending Tweet: %s" %e)
            return False

        return True

    def _notifyTwitter(self, message='', force=False):
        prefix = orielpy.TWITTER_PREFIX

        if not orielpy.TWITTER_ENABLED and not force:
            return False

        return self._send_tweet(prefix+": "+message)

notifier = TwitterNotifier
